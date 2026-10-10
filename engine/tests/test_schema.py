"""Schema contract tests: validation, uniqueness, determinism, round-trip."""
import pytest

from fs_quiz.schema import (
    SCHEMA_VERSION, DOMAINS, Question, make_qid,
)


def _q(**kw):
    base = dict(
        qid="abc123def456",
        schema_version=SCHEMA_VERSION,
        domain="survey-computations",
        topic="inverse",
        difficulty=2,
        stem="What is 2+2?",
        choices=("3", "4", "5", "6"),
        answer_index=1,
        explanation="Because.",
        parameters={},
        seed=0,
    )
    base.update(kw)
    return Question(**base)


def test_valid_question():
    q = _q()
    assert q.correct_choice == "4"
    assert q.grade(1) is True
    assert q.grade(0) is False


def test_rejects_duplicate_choices():
    with pytest.raises(ValueError):
        _q(choices=("3", "4", "4", "6"))


def test_rejects_bad_schema_version():
    with pytest.raises(ValueError):
        _q(schema_version=999)


def test_rejects_unknown_domain():
    with pytest.raises(ValueError):
        _q(domain="not-a-domain")


def test_rejects_bad_answer_index():
    with pytest.raises(ValueError):
        _q(answer_index=4)


def test_json_round_trip():
    q = _q()
    assert Question.from_json(q.to_json()) == q


def test_make_qid_stable_and_unique():
    assert make_qid("g", 1, 2) == make_qid("g", 1, 2)
    assert make_qid("g", 1, 2) != make_qid("g", 1, 3)
    assert make_qid("g", 1, 2) != make_qid("h", 1, 2)
    assert len(make_qid("g", 1, 2)) == 12


def test_domains_cover_all_seven_fs_areas():
    assert len(DOMAINS) == 7
    assert "survey-computations" in DOMAINS
    assert "boundary-law-and-real-property" in DOMAINS
