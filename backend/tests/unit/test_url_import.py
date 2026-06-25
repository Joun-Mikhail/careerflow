"""Unit tests for the URL job-posting extractor.

The fetcher is injected, so these tests exercise the full extraction pipeline
without touching the network.
"""

from __future__ import annotations

from app.services.url_import import extract_from_html, extract_from_url

_JSONLD_PAGE = """
<!doctype html>
<html><head>
<title>Senior Backend Engineer at Acme Co</title>
<meta property="og:title" content="Senior Backend Engineer">
<meta property="og:site_name" content="Acme Co">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "Senior Backend Engineer",
  "description": "<p>Build distributed systems in Python.</p><ul><li>FastAPI</li></ul>",
  "datePosted": "2026-06-01T00:00:00Z",
  "hiringOrganization": {"@type": "Organization", "name": "Acme Co"},
  "jobLocation": {
    "@type": "Place",
    "address": {
      "addressLocality": "Berlin",
      "addressRegion": "BE",
      "addressCountry": "DE"
    }
  },
  "jobLocationType": "TELECOMMUTE",
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "EUR",
    "value": {"@type": "QuantitativeValue", "minValue": 80000, "maxValue": 110000}
  }
}
</script>
</head><body>Apply now</body></html>
"""


def test_extracts_jsonld_jobposting() -> None:
    result = extract_from_html(_JSONLD_PAGE, source_url="https://boards.greenhouse.io/acme/jobs/1")

    assert result.role_title == "Senior Backend Engineer"
    assert result.company_name == "Acme Co"
    assert result.location == "Berlin, BE, DE"
    assert result.is_remote is True
    assert result.salary_min == 80000
    assert result.salary_max == 110000
    assert result.salary_currency == "EUR"
    assert result.description is not None
    assert "FastAPI" in result.description
    assert "<" not in result.description  # HTML stripped
    assert result.source == "Greenhouse"
    assert result.application_url == "https://boards.greenhouse.io/acme/jobs/1"
    assert result.posted_at is not None


def test_falls_back_to_og_meta_when_no_jsonld() -> None:
    html = """
    <html><head>
      <title>Cool Job</title>
      <meta property="og:title" content="Staff Engineer">
      <meta property="og:site_name" content="Hooli">
      <meta property="og:description" content="A great remote role.">
    </head><body></body></html>
    """
    result = extract_from_html(html, source_url="https://example.com/jobs/2")
    assert result.role_title == "Staff Engineer"
    assert result.company_name == "Hooli"
    assert result.description == "A great remote role."
    # The body text mentions "remote" via the og:description, so the
    # whole-page text fallback flips is_remote True.
    assert result.is_remote is True
    assert result.salary_min is None


def test_handles_garbage_jsonld_gracefully() -> None:
    html = """
    <html><head>
      <title>Junior Dev</title>
      <script type="application/ld+json">{not valid json at all</script>
      <meta name="description" content="Entry level role">
    </head><body></body></html>
    """
    result = extract_from_html(html, source_url="https://example.com/x")
    # Falls through to <title>; never raises.
    assert result.role_title == "Junior Dev"
    assert result.description == "Entry level role"


def test_extract_from_url_uses_injected_fetcher() -> None:
    captured: list[str] = []

    def fake_fetcher(url: str) -> str:
        captured.append(url)
        return _JSONLD_PAGE

    result = extract_from_url("https://jobs.lever.co/acme/1", fetcher=fake_fetcher)
    assert captured == ["https://jobs.lever.co/acme/1"]
    assert result.role_title == "Senior Backend Engineer"
    assert result.source == "Lever"


def test_jsonld_in_graph_array() -> None:
    html = """
    <html><head><script type="application/ld+json">
    {"@context":"https://schema.org","@graph":[
      {"@type":"WebPage","name":"x"},
      {"@type":"JobPosting","title":"Data Scientist",
       "hiringOrganization":{"name":"Globex"}}
    ]}
    </script></head></html>
    """
    result = extract_from_html(html, source_url="https://example.com")
    assert result.role_title == "Data Scientist"
    assert result.company_name == "Globex"


def test_salary_normalized_when_inverted() -> None:
    html = """
    <html><head><script type="application/ld+json">
    {"@type":"JobPosting","title":"X",
     "baseSalary":{"currency":"USD","value":{"minValue":200000,"maxValue":50000}}}
    </script></head></html>
    """
    result = extract_from_html(html, source_url="https://example.com")
    # We clamp max to min instead of letting a bad source produce an invalid range.
    assert result.salary_min == 200000
    assert result.salary_max == 200000
