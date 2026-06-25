"""AI provider abstraction for CV tailoring.

A single :class:`AiProvider` protocol has two implementations:

* :class:`OpenAiProvider` — calls OpenAI (gpt-4o-mini by default). ``openai`` is
  imported lazily so the dependency is only touched when a key is configured.
* :class:`StubProvider` — a deterministic, offline fallback used whenever no
  API key is set, so the whole tailoring flow works in development and tests
  without network calls or cost.

:func:`get_ai_provider` picks the implementation from configuration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from app.core.config import get_settings

settings = get_settings()

_SYSTEM_PROMPT = (
    "You are an expert technical recruiter and CV writer. Rewrite the candidate's "
    "CV so it is tailored to the target job: emphasise the most relevant experience "
    "and skills, mirror the job's terminology where truthful, and keep it concise and "
    "honest. Never invent experience, employers, or qualifications the candidate does "
    "not have. Respond with a JSON object containing the keys 'tailored_cv' and "
    "'cover_letter' (cover_letter may be an empty string when not requested)."
)


@dataclass(frozen=True)
class TailorResult:
    """The output of a tailoring request."""

    tailored_cv: str
    cover_letter: str | None
    provider: str


class AiProvider(Protocol):
    """Produces a tailored CV (and optional cover letter) from inputs."""

    name: str

    def tailor_cv(
        self, *, cv_text: str, job_description: str, include_cover_letter: bool
    ) -> TailorResult: ...


class StubProvider:
    """Deterministic offline provider (no API key required).

    Produces a clearly-labelled, structured rewrite by re-framing the CV around
    the job description's keywords. Good enough to exercise the full flow and
    keep tests hermetic; it never calls the network.
    """

    name = "stub"

    def tailor_cv(
        self, *, cv_text: str, job_description: str, include_cover_letter: bool
    ) -> TailorResult:
        keywords = _top_keywords(job_description)
        focus = ", ".join(keywords) if keywords else "the role's core requirements"
        tailored = (
            f"PROFESSIONAL SUMMARY (tailored for: {focus})\n"
            f"{_first_sentence(cv_text)}\n\n"
            f"{cv_text.strip()}\n\n"
            f"— Tailored highlights aligned to: {focus}."
        )
        cover_letter = None
        if include_cover_letter:
            cover_letter = (
                "Dear Hiring Manager,\n\n"
                "I'm excited to apply for this role. My background aligns closely "
                f"with your needs around {focus}. I'd welcome the chance to discuss "
                "how I can contribute.\n\nBest regards"
            )
        return TailorResult(tailored_cv=tailored, cover_letter=cover_letter, provider=self.name)


class OpenAiProvider:
    """Tailors a CV using OpenAI chat completions."""

    name = "openai"

    def tailor_cv(
        self, *, cv_text: str, job_description: str, include_cover_letter: bool
    ) -> TailorResult:
        from openai import OpenAI  # lazy import; only needed when a key is set

        client = OpenAI(api_key=settings.openai_api_key)
        user_prompt = (
            f"TARGET JOB DESCRIPTION:\n{job_description}\n\n"
            f"CANDIDATE CV:\n{cv_text}\n\n"
            f"Include a cover letter: {'yes' if include_cover_letter else 'no'}."
        )
        completion = client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
        payload = json.loads(completion.choices[0].message.content or "{}")
        cover = payload.get("cover_letter") or None
        return TailorResult(
            tailored_cv=payload.get("tailored_cv", "").strip(),
            cover_letter=cover.strip() if isinstance(cover, str) and include_cover_letter else None,
            provider=self.name,
        )


def get_ai_provider() -> AiProvider:
    """Return the configured AI provider (OpenAI when keyed, else the stub)."""
    if settings.ai_enabled:
        return OpenAiProvider()
    return StubProvider()


def _first_sentence(text: str) -> str:
    stripped = text.strip()
    for sep in (". ", "\n"):
        if sep in stripped:
            return stripped.split(sep, 1)[0].strip()
    return stripped[:200]


def _top_keywords(text: str, limit: int = 6) -> list[str]:
    """Cheap keyword extraction for the stub: most frequent salient words."""
    stop = {
        "the",
        "and",
        "for",
        "with",
        "you",
        "your",
        "are",
        "our",
        "this",
        "that",
        "will",
        "have",
        "from",
        "job",
        "role",
        "team",
        "work",
        "must",
        "should",
        "experience",
        "years",
        "ability",
        "strong",
        "good",
        "plus",
        "etc",
    }
    counts: dict[str, int] = {}
    for raw in text.lower().split():
        word = "".join(ch for ch in raw if ch.isalnum())
        if len(word) < 4 or word in stop:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts, key=lambda w: counts[w], reverse=True)
    return ranked[:limit]
