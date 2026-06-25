"""Extract job-posting fields from a public URL.

Fetches a job-ad page and pulls structured data out of it using, in order:

1. ``<script type="application/ld+json">`` blocks following the schema.org
   ``JobPosting`` shape — emitted by most ATS (Greenhouse, Lever, Workday,
   LinkedIn, Indeed) and the most reliable signal we have.
2. OpenGraph / standard ``<meta>`` tags for title and description.
3. ``<title>`` as a last-resort role-title source.

Returns an :class:`ExtractedJob` with whatever could be parsed; the caller
decides what to do with partial data. The fetcher is injected so tests can
exercise extraction without touching the network.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from html import unescape

DEFAULT_TIMEOUT = 10.0
MAX_BYTES = 1_500_000  # ~1.5 MB cap; most job pages are well under this
MAX_DESCRIPTION_LEN = 8000


@dataclass(frozen=True)
class ExtractedJob:
    """A best-effort, normalized view of a fetched job posting."""

    role_title: str | None
    company_name: str | None
    location: str | None
    is_remote: bool
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    description: str | None
    application_url: str
    source: str | None
    posted_at: datetime | None


Fetcher = Callable[[str], str]


def _default_fetcher(url: str) -> str:
    import httpx

    headers = {
        # Several ATS reject default httpx UA; mimic a normal browser.
        "User-Agent": ("Mozilla/5.0 (compatible; CareerFlowBot/1.0; +https://careerflow.app)"),
        "Accept": "text/html,application/xhtml+xml",
    }
    with httpx.Client(follow_redirects=True, timeout=DEFAULT_TIMEOUT, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        # Cap to avoid pulling huge pages into memory.
        return response.text[:MAX_BYTES]


def extract_from_url(url: str, *, fetcher: Fetcher | None = None) -> ExtractedJob:
    """Fetch ``url`` and pull job-posting fields out of its HTML."""
    html = (fetcher or _default_fetcher)(url)
    return extract_from_html(html, source_url=url)


def extract_from_html(html: str, *, source_url: str) -> ExtractedJob:
    """Parse already-fetched HTML — separated for testability."""
    posting = _find_job_posting_jsonld(html)
    og = _extract_og_meta(html)
    title_tag = _extract_title_tag(html)

    role_title = _pick_role_title(posting, og, title_tag)
    company_name = _pick_company(posting, og)
    location, is_remote = _pick_location(posting, html)
    salary_min, salary_max, salary_currency = _pick_salary(posting)
    description = _pick_description(posting, og)
    posted_at = _pick_posted_at(posting)
    source = _infer_source(source_url)

    return ExtractedJob(
        role_title=role_title,
        company_name=company_name,
        location=location,
        is_remote=is_remote,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        description=description,
        application_url=source_url,
        source=source,
        posted_at=posted_at,
    )


# -- JSON-LD ------------------------------------------------------------------

_JSONLD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)


def _find_job_posting_jsonld(html: str) -> dict | None:
    """Return the first JSON-LD block whose @type includes ``JobPosting``."""
    for match in _JSONLD_RE.finditer(html):
        raw = match.group(1).strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Some pages embed multiple JSON objects in one block; skip.
            continue
        found = _find_jobposting_node(data)
        if found is not None:
            return found
    return None


def _find_jobposting_node(node: object) -> dict | None:
    if isinstance(node, list):
        for item in node:
            result = _find_jobposting_node(item)
            if result is not None:
                return result
        return None
    if isinstance(node, dict):
        types = node.get("@type")
        if isinstance(types, str) and types == "JobPosting":
            return node
        if isinstance(types, list) and "JobPosting" in types:
            return node
        # Nested @graph (common in Yoast-style output).
        graph = node.get("@graph")
        if isinstance(graph, list):
            return _find_jobposting_node(graph)
    return None


# -- Field pickers -----------------------------------------------------------


def _pick_role_title(posting: dict | None, og: dict[str, str], title_tag: str | None) -> str | None:
    if posting:
        title = posting.get("title")
        if isinstance(title, str) and title.strip():
            return _clip(title.strip(), 200)
    if og.get("title"):
        return _clip(og["title"], 200)
    if title_tag:
        return _clip(title_tag, 200)
    return None


def _pick_company(posting: dict | None, og: dict[str, str]) -> str | None:
    if posting:
        org = posting.get("hiringOrganization")
        if isinstance(org, dict):
            name = org.get("name")
            if isinstance(name, str) and name.strip():
                return _clip(name.strip(), 200)
        elif isinstance(org, str) and org.strip():
            return _clip(org.strip(), 200)
    site_name = og.get("site_name")
    if site_name:
        return _clip(site_name, 200)
    return None


def _pick_location(posting: dict | None, html: str) -> tuple[str | None, bool]:
    location: str | None = None
    is_remote = False
    if posting:
        loc_node = posting.get("jobLocation")
        location = _flatten_location(loc_node)
        job_type = posting.get("jobLocationType")
        if isinstance(job_type, str) and "TELECOMMUTE" in job_type.upper():
            is_remote = True
    if not is_remote and re.search(r"\bremote\b", html, re.IGNORECASE):
        # Hint only; cheap text check on the (already capped) page body.
        is_remote = True
    return location, is_remote


def _flatten_location(node: object) -> str | None:
    if isinstance(node, list):
        for item in node:
            result = _flatten_location(item)
            if result:
                return result
        return None
    if not isinstance(node, dict):
        return None
    address = node.get("address")
    if isinstance(address, dict):
        parts = [
            address.get("addressLocality"),
            address.get("addressRegion"),
            address.get("addressCountry"),
        ]
        text = ", ".join(p for p in parts if isinstance(p, str) and p.strip())
        if text:
            return _clip(text, 200)
    name = node.get("name")
    if isinstance(name, str) and name.strip():
        return _clip(name.strip(), 200)
    return None


def _pick_salary(posting: dict | None) -> tuple[int | None, int | None, str | None]:
    if not posting:
        return None, None, None
    salary_node = posting.get("baseSalary")
    if not isinstance(salary_node, dict):
        return None, None, None
    raw_currency = salary_node.get("currency")
    currency = raw_currency.strip().upper()[:3] or None if isinstance(raw_currency, str) else None
    value = salary_node.get("value")
    if not isinstance(value, dict):
        return None, None, currency
    salary_min = _coerce_money(value.get("minValue"))
    salary_max = _coerce_money(value.get("maxValue"))
    if salary_min is None and salary_max is None:
        single = _coerce_money(value.get("value"))
        if single is not None:
            salary_min = salary_max = single
    if salary_min is not None and salary_max is not None and salary_max < salary_min:
        salary_max = salary_min
    return salary_min, salary_max, currency


def _coerce_money(raw: object) -> int | None:
    if isinstance(raw, bool):  # bools are ints in Python — exclude explicitly
        return None
    if isinstance(raw, (int, float)):
        return int(raw) if raw > 0 else None
    if isinstance(raw, str):
        cleaned = re.sub(r"[^0-9.]", "", raw)
        if not cleaned:
            return None
        try:
            number = float(cleaned)
        except ValueError:
            return None
        return int(number) if number > 0 else None
    return None


def _pick_description(posting: dict | None, og: dict[str, str]) -> str | None:
    if posting:
        desc = posting.get("description")
        if isinstance(desc, str) and desc.strip():
            return _clip(_html_to_text(desc), MAX_DESCRIPTION_LEN)
    if og.get("description"):
        return _clip(og["description"], MAX_DESCRIPTION_LEN)
    return None


def _pick_posted_at(posting: dict | None) -> datetime | None:
    if not posting:
        return None
    raw = posting.get("datePosted")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _infer_source(url: str) -> str | None:
    """Friendly source name from the host (e.g. ``linkedin.com`` → ``LinkedIn``)."""
    host_match = re.match(r"https?://(?:www\.)?([^/]+)", url, re.IGNORECASE)
    if not host_match:
        return None
    host = host_match.group(1).lower()
    known = {
        "linkedin.com": "LinkedIn",
        "indeed.com": "Indeed",
        "glassdoor.com": "Glassdoor",
        "greenhouse.io": "Greenhouse",
        "boards.greenhouse.io": "Greenhouse",
        "lever.co": "Lever",
        "jobs.lever.co": "Lever",
        "workday.com": "Workday",
        "myworkdayjobs.com": "Workday",
        "wellfound.com": "Wellfound",
        "ycombinator.com": "Y Combinator",
        "stackoverflow.com": "Stack Overflow",
        "remote.co": "Remote.co",
        "weworkremotely.com": "We Work Remotely",
        "ashbyhq.com": "Ashby",
        "smartrecruiters.com": "SmartRecruiters",
    }
    for needle, label in known.items():
        if host.endswith(needle):
            return label
    # Fall back to bare domain (e.g. ``acme.com``).
    return host[:120]


# -- HTML helpers ------------------------------------------------------------

_META_RE = re.compile(
    r"<meta\s+(?P<attrs>[^>]+?)\s*/?>",
    re.IGNORECASE | re.DOTALL,
)
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _extract_og_meta(html: str) -> dict[str, str]:
    """Extract a flat ``{name: content}`` view of meta tags we care about."""
    wanted = {"og:title", "og:description", "og:site_name", "description"}
    out: dict[str, str] = {}
    for match in _META_RE.finditer(html):
        attrs = _parse_attrs(match.group("attrs"))
        name = attrs.get("property") or attrs.get("name")
        content = attrs.get("content")
        if not name or content is None:
            continue
        if name not in wanted:
            continue
        key = name.split(":", 1)[1] if name.startswith("og:") else name
        if key not in out:
            out[key] = _clip(unescape(content).strip(), MAX_DESCRIPTION_LEN)
    return out


_ATTR_RE = re.compile(r'(\w[\w:-]*)\s*=\s*"([^"]*)"|\s*(\w[\w:-]*)\s*=\s*\'([^\']*)\'')


def _parse_attrs(raw: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in _ATTR_RE.finditer(raw):
        key = (match.group(1) or match.group(3) or "").lower()
        value = match.group(2) if match.group(2) is not None else match.group(4) or ""
        if key:
            attrs[key] = value
    return attrs


def _extract_title_tag(html: str) -> str | None:
    match = _TITLE_RE.search(html)
    if not match:
        return None
    text = unescape(_TAG_RE.sub("", match.group(1))).strip()
    return text or None


def _html_to_text(html: str) -> str:
    no_tags = _TAG_RE.sub(" ", html)
    return _WHITESPACE_RE.sub(" ", unescape(no_tags)).strip()


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
