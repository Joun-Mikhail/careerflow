"""Unit tests for the deterministic CV-to-job match scorer."""

from __future__ import annotations

from app.services.matching import score_match

BACKEND_JOB = """
    We are hiring a Senior Backend Engineer to work on our payments platform.
    You will build services in Python with FastAPI and PostgreSQL, deploy them
    on AWS using Docker and Kubernetes, and help the team adopt better testing.
    Experience with Redis and Kafka is a plus.
"""

STRONG_CV = """
    Senior software engineer with eight years building payments systems.
    Day to day I write Python and FastAPI services backed by PostgreSQL and
    Redis, containerise them with Docker, and run them on AWS and Kubernetes.
    I introduced unit testing and code review practices to my last team, and
    have worked with Kafka for event streaming.
"""

WEAK_CV = """
    Graphic designer with six years of experience in branding and print.
    I work daily in Illustrator and Photoshop, run client workshops, and
    manage delivery timelines for marketing campaigns.
"""


class TestScoreMatch:
    def test_a_closely_matching_cv_scores_strong(self) -> None:
        result = score_match(cv_text=STRONG_CV, job_description=BACKEND_JOB)
        assert result.score >= 75
        assert result.verdict == "strong"

    def test_an_unrelated_cv_scores_far_lower(self) -> None:
        strong = score_match(cv_text=STRONG_CV, job_description=BACKEND_JOB)
        weak = score_match(cv_text=WEAK_CV, job_description=BACKEND_JOB)
        assert weak.score < strong.score
        assert weak.verdict == "stretch"

    def test_it_names_the_skills_it_matched_and_missed(self) -> None:
        cv = "I write Python and use PostgreSQL every day."
        result = score_match(cv_text=cv, job_description=BACKEND_JOB)
        assert "python" in result.matched_skills
        assert "postgresql" in result.matched_skills
        # Named by the posting, absent from the CV — the actionable half.
        assert "kubernetes" in result.missing_skills
        assert "kubernetes" not in result.matched_skills

    def test_scoring_is_deterministic(self) -> None:
        first = score_match(cv_text=STRONG_CV, job_description=BACKEND_JOB)
        second = score_match(cv_text=STRONG_CV, job_description=BACKEND_JOB)
        assert first == second

    def test_it_is_case_insensitive(self) -> None:
        upper = score_match(cv_text=STRONG_CV.upper(), job_description=BACKEND_JOB)
        normal = score_match(cv_text=STRONG_CV, job_description=BACKEND_JOB)
        assert upper.score == normal.score

    def test_skill_matching_respects_word_boundaries(self) -> None:
        # "go" must not be found inside "going", or every CV matches Go.
        job = "We need someone strong in Go, Rust and Kubernetes for our platform."
        cv = "I am going to the shops. I enjoy gardening and good conversation."
        result = score_match(cv_text=cv, job_description=job)
        assert "go" not in result.matched_skills

    def test_an_empty_job_description_does_not_error(self) -> None:
        result = score_match(cv_text=STRONG_CV, job_description="")
        assert 0 <= result.score <= 100


class TestSeniority:
    def test_matching_levels_score_full_marks(self) -> None:
        result = score_match(
            cv_text="Senior engineer with Python and AWS and Docker experience.",
            job_description="Senior engineer wanted, Python, AWS, Docker.",
        )
        assert result.job_seniority == "senior"
        assert result.cv_seniority == "senior"
        assert result.breakdown.seniority == 100

    def test_distant_levels_are_penalised(self) -> None:
        aligned = score_match(
            cv_text="Senior engineer, Python, AWS, Docker.",
            job_description="Senior engineer, Python, AWS, Docker.",
        )
        mismatched = score_match(
            cv_text="Intern learning Python, AWS and Docker.",
            job_description="Senior engineer, Python, AWS, Docker.",
        )
        assert mismatched.breakdown.seniority < aligned.breakdown.seniority

    def test_an_unstated_level_is_neutral_not_punished(self) -> None:
        result = score_match(
            cv_text="I build things with Python, AWS and Docker.",
            job_description="We use Python, AWS and Docker.",
        )
        assert result.cv_seniority is None
        assert result.breakdown.seniority == 75


class TestThinPostings:
    def test_a_posting_naming_no_skills_leans_on_keywords(self) -> None:
        # Nothing from the skill vocabulary appears, so the skill component is
        # sidelined rather than scoring zero and dragging the total down.
        job = "Seeking a warm, organised bookshop manager for our riverside branch."
        cv = "Organised bookshop manager, riverside branch experience, warm with customers."
        result = score_match(cv_text=cv, job_description=job)
        assert result.score >= 50

    def test_a_posting_with_no_skills_reports_none_missing(self) -> None:
        job = "Seeking a warm, organised bookshop manager."
        result = score_match(cv_text="Unrelated text.", job_description=job)
        assert result.missing_skills == []
