"""Engine tests: generation, bank round-trip, grading, replay stability."""
import os

from fs_quiz import registry
from fs_quiz.engine import QuizEngine


def test_generate_replays_exactly():
    eng = QuizEngine()
    a = eng.generate("survey-computations", "inverse", n=5, seed=4)
    b = eng.generate("survey-computations", "inverse", n=5, seed=4)
    assert [q.qid for q in a] == [q.qid for q in b]
    assert [q.to_json() for q in a] == [q.to_json() for q in b]


def test_generate_bank_covers_all_registered_topics(tmp_path):
    eng = QuizEngine()
    bank = eng.generate_bank(n_per_topic=2, seed=0)
    topics = {(q.domain, q.topic) for q in bank}
    assert ("survey-computations", "inverse") in topics
    assert ("boundary-law-and-real-property", "hierarchy-of-calls") in topics
    n_topics = sum(len(registry.list_topics(d)) for d in registry.list_domains())
    assert len(bank) == n_topics * 2
    assert len({q.qid for q in bank}) == len(bank)  # qids unique


def test_export_import_round_trip(tmp_path):
    eng = QuizEngine()
    bank = eng.generate("survey-computations", "stadia", n=4, seed=9)
    path = str(tmp_path / "bank.json")
    eng.export_bank(bank, path)
    back = eng.import_bank(path)
    assert [q.qid for q in back] == [q.qid for q in bank]
    assert back[0].correct_choice == bank[0].correct_choice


def test_import_rejects_wrong_schema(tmp_path):
    import json
    path = str(tmp_path / "bad.json")
    with open(path, "w") as f:
        json.dump({"schema_version": 999, "questions": []}, f)
    eng = QuizEngine()
    try:
        eng.import_bank(path)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_grading():
    eng = QuizEngine()
    bank = eng.generate("survey-computations", "level-notes", n=3, seed=1)
    answers = {q.qid: q.answer_index for q in bank}  # all correct
    s = eng.grade(bank, answers)
    assert s["total"] == 3 and s["correct"] == 3 and s["score_pct"] == 100.0
    answers[bank[0].qid] = (bank[0].answer_index + 1) % 4  # one wrong
    s = eng.grade(bank, answers)
    assert s["correct"] == 2
