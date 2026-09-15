"""Deterministic CV-to-job match scoring.

Scores how well a CV answers a job posting, with no API key, no network call,
and no model: the same inputs always produce the same score, and every number
is traceable to words that are actually present in the two texts. That keeps
the feature available to every user and keeps the explanation honest — the
output names the skills it matched and the ones it did not, rather than
asking anyone to trust an opaque percentage.

Three components make up the score:

* **Skills** — which of the skills named in the posting appear in the CV. This
  carries the most weight, because a named skill is the clearest signal a
  posting gives about what it wants.
* **Keywords** — coverage of the posting's other salient terms, which catches
  domain language a fixed skill vocabulary cannot ("fintech", "marketplace").
* **Seniority** — whether the levels implied by the two texts line up, so a
  senior CV is not reported as a perfect match for an internship.

The weights below are a deliberate judgement, not a fitted model, and the
breakdown is returned alongside the total so a user can see how it was reached.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Weights sum to 1.0. Skills dominate; seniority only nudges.
_SKILL_WEIGHT = 0.55
_KEYWORD_WEIGHT = 0.30
_SENIORITY_WEIGHT = 0.15

# Verdict thresholds, expressed as the lowest score that earns each label.
_STRONG_MATCH = 75
_PROMISING_MATCH = 50

# A posting that names very few skills gives a thin signal, so the skill
# component is only trusted once at least this many are found.
_MIN_SKILLS_FOR_SIGNAL = 3

# Recognised skills, grouped only for readability. Multi-word entries are
# matched as phrases; the rest match on word boundaries, so "go" does not
# match "going" and "r" does not match every stray letter.
_SKILLS: frozenset[str] = frozenset(
    {
        # Languages
        "python",
        "javascript",
        "typescript",
        "java",
        "kotlin",
        "swift",
        "go",
        "golang",
        "rust",
        "ruby",
        "php",
        "c#",
        "c++",
        "scala",
        "elixir",
        "sql",
        # Frontend
        "react",
        "vue",
        "angular",
        "svelte",
        "next.js",
        "nuxt",
        "redux",
        "tailwind",
        "css",
        "html",
        "webpack",
        "vite",
        # Backend and data
        "django",
        "flask",
        "fastapi",
        "spring",
        "rails",
        "node.js",
        "express",
        "graphql",
        "rest",
        "grpc",
        "postgresql",
        "postgres",
        "mysql",
        "mongodb",
        "redis",
        "elasticsearch",
        "kafka",
        "rabbitmq",
        "spark",
        "airflow",
        # Cloud and platform
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
        "ansible",
        "jenkins",
        "github actions",
        "gitlab ci",
        "ci/cd",
        "linux",
        "nginx",
        "serverless",
        "lambda",
        # Data and ML
        "pandas",
        "numpy",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "machine learning",
        "deep learning",
        "nlp",
        "data analysis",
        "tableau",
        "power bi",
        "dbt",
        # Practice
        "agile",
        "scrum",
        "kanban",
        "tdd",
        "microservices",
        "rest api",
        "unit testing",
        "code review",
        "git",
        "jira",
        "figma",
        "accessibility",
    }
)

# Ordered least to most senior; the index is the distance used for scoring.
_SENIORITY_LADDER: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("intern", ("intern", "internship", "placement", "trainee")),
    ("junior", ("junior", "graduate", "entry level", "entry-level", "associate")),
    ("mid", ("mid level", "mid-level", "intermediate")),
    ("senior", ("senior", "sr.", "sr ")),
    ("staff", ("staff", "principal", "lead", "head of", "director")),
)

# Words too generic to say anything about fit. Job ads are full of them.
_STOPWORDS: frozenset[str] = frozenset(
    {
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
        "we",
        "us",
        "who",
        "what",
        "their",
        "they",
        "them",
        "about",
        "into",
        "than",
        "been",
        "were",
        "would",
        "could",
        "also",
        "more",
        "most",
        "such",
        "some",
        "any",
        "all",
        "can",
        "may",
        "new",
        "using",
        "use",
        "well",
        "help",
        "including",
        "across",
        "within",
        "while",
        "when",
        "where",
        "how",
        "why",
        "company",
        "candidate",
        "candidates",
        "applicant",
        "position",
        "opportunity",
        "looking",
        "join",
        "hiring",
        "apply",
        "please",
        "benefits",
        "salary",
        "responsibilities",
        "requirements",
        "qualifications",
        "skills",
        "working",
    }
)

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9+#./-]*")


@dataclass(frozen=True)
class MatchBreakdown:
    """The component scores behind an overall match, each 0-100."""

    skills: int
    keywords: int
    seniority: int


@dataclass(frozen=True)
class MatchResult:
    """A scored comparison of one CV against one job posting."""

    score: int
    verdict: str
    matched_skills: list[str]
    missing_skills: list[str]
    missing_keywords: list[str]
    breakdown: MatchBreakdown
    job_seniority: str | None
    cv_seniority: str | None


def score_match(*, cv_text: str, job_description: str) -> MatchResult:
    """Score how well ``cv_text`` answers ``job_description``.

    Both texts are compared case-insensitively. An empty job description yields
    a zero score rather than an error, since a posting with no text simply
    offers nothing to match against.
    """
    cv = cv_text.lower()
    job = job_description.lower()

    job_skills = _skills_in(job)
    cv_skills = _skills_in(cv)
    matched_skills = sorted(job_skills & cv_skills)
    missing_skills = sorted(job_skills - cv_skills)

    job_keywords = _salient_keywords(job)
    cv_words = set(_WORD_RE.findall(cv))
    matched_keywords = [word for word in job_keywords if word in cv_words]
    missing_keywords = [word for word in job_keywords if word not in cv_words]

    job_level = _seniority_of(job)
    cv_level = _seniority_of(cv)

    skills_score = _ratio(len(matched_skills), len(job_skills))
    keyword_score = _ratio(len(matched_keywords), len(job_keywords))
    seniority_score = _seniority_score(job_level, cv_level)

    # A posting naming almost no skills says little, so lean on keywords rather
    # than let one or two incidental terms swing the whole score.
    if len(job_skills) < _MIN_SKILLS_FOR_SIGNAL:
        skill_weight = 0.0
        keyword_weight = _SKILL_WEIGHT + _KEYWORD_WEIGHT
    else:
        skill_weight = _SKILL_WEIGHT
        keyword_weight = _KEYWORD_WEIGHT

    total = (
        skills_score * skill_weight
        + keyword_score * keyword_weight
        + seniority_score * _SENIORITY_WEIGHT
    )
    score = round(total)

    return MatchResult(
        score=score,
        verdict=_verdict(score),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        # The actionable half: what to address before applying.
        missing_keywords=missing_keywords[:10],
        breakdown=MatchBreakdown(
            skills=round(skills_score),
            keywords=round(keyword_score),
            seniority=round(seniority_score),
        ),
        job_seniority=job_level,
        cv_seniority=cv_level,
    )


def _verdict(score: int) -> str:
    if score >= _STRONG_MATCH:
        return "strong"
    if score >= _PROMISING_MATCH:
        return "promising"
    return "stretch"


def _ratio(matched: int, total: int) -> float:
    """Percentage matched, treating "nothing to match" as full marks.

    A posting that names no skills should not drag a CV down for failing to
    mention skills that were never asked for.
    """
    if total == 0:
        return 100.0
    return (matched / total) * 100.0


def _skills_in(text: str) -> set[str]:
    """Skills from the vocabulary that appear in ``text``."""
    found: set[str] = set()
    for skill in _SKILLS:
        if " " in skill or "/" in skill:
            # Phrases: a plain substring test is right, and avoids escaping pain.
            if skill in text:
                found.add(skill)
        elif re.search(rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])", text):
            found.add(skill)
    return found


def _salient_keywords(text: str, limit: int = 25) -> list[str]:
    """The most frequent meaningful words in ``text``, most frequent first."""
    counts: dict[str, int] = {}
    for word in _WORD_RE.findall(text):
        if len(word) < 4 or word in _STOPWORDS or word.isdigit():
            continue
        counts[word] = counts.get(word, 0) + 1
    # Sort by frequency, then alphabetically, so the result is stable.
    ranked = sorted(counts, key=lambda w: (-counts[w], w))
    return ranked[:limit]


def _seniority_of(text: str) -> str | None:
    """The most senior level named in ``text``, or None when none is."""
    found: str | None = None
    for level, markers in _SENIORITY_LADDER:
        if any(marker in text for marker in markers):
            found = level
    return found


def _seniority_score(job_level: str | None, cv_level: str | None) -> float:
    """How well two seniority levels line up, 0-100.

    When either side is silent about level the score is neutral rather than
    punitive — plenty of good CVs never use the word "senior".
    """
    if job_level is None or cv_level is None:
        return 75.0
    order = [level for level, _ in _SENIORITY_LADDER]
    distance = abs(order.index(job_level) - order.index(cv_level))
    return max(0.0, 100.0 - distance * 25.0)
