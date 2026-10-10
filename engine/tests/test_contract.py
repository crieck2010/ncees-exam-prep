"""v1 contract lock tests. These are intentionally brittle: any change that
alters generation output, field names, or validation MUST fail here, forcing
an explicit schema-version bump instead of a silent break.
"""
import json
import os

import pytest

from fs_quiz import registry
from fs_quiz.contract import validate_bank_dict, validate_question_dict
from fs_quiz.engine import QuizEngine
from fs_quiz.interop import flutter_contract
from fs_quiz.schema import SCHEMA_VERSION

GOLDEN = os.path.join(os.path.dirname(__file__), "fixtures", "bank-v1-golden.json")


def test_schema_version_is_one():
    assert SCHEMA_VERSION == 1


def test_golden_bank_imports_cleanly():
    eng = QuizEngine()
    bank = eng.import_bank(GOLDEN)
    assert len(bank) == 96  # 48 topics x 2, frozen at v1.0.0


def test_golden_bank_reexports_byte_identical(tmp_path):
    """The lock: re-exporting the golden bank must reproduce it exactly."""
    eng = QuizEngine()
    bank = eng.import_bank(GOLDEN)
    out = str(tmp_path / "reexport.json")
    eng.export_bank(bank, out)
    with open(GOLDEN, "rb") as f:
        golden_bytes = f.read()
    with open(out, "rb") as f:
        reexport_bytes = f.read()
    assert reexport_bytes == golden_bytes


def test_golden_bank_passes_contract_validation():
    with open(GOLDEN) as f:
        payload = json.load(f)
    assert validate_bank_dict(payload) == []


def test_contract_rejects_mutations():
    eng = QuizEngine()
    bank = eng.generate("survey-computations", "inverse", n=1, seed=0)
    q = bank[0].to_dict()

    bad = dict(q)
    del bad["explanation"]
    assert validate_question_dict(bad)

    bad = dict(q)
    bad["choices"] = ["a", "b", "c", "a"]
    assert validate_question_dict(bad)

    bad = dict(q)
    bad["answer_index"] = 7
    assert validate_question_dict(bad)

    bad = dict(q)
    bad["schema_version"] = 2
    assert validate_question_dict(bad)

    payload = {"schema_version": 1, "generator": "x", "engine_version": "1.0.0",
               "question_count": 2, "questions": [q]}
    assert validate_bank_dict(payload)  # count mismatch

    payload = {"schema_version": 1, "generator": "x", "engine_version": "1.0.0",
               "question_count": 1, "questions": [q, q]}
    assert validate_bank_dict(payload)  # duplicate qid


def test_flutter_contract_shape_is_stable():
    c = flutter_contract()
    assert c["schema_version"] == 1
    assert set(c["bank_file"]) == {"schema_version", "generator",
                                   "engine_version", "question_count", "questions"}
    assert set(c["question"]) == {"qid", "schema_version", "domain", "topic",
                                  "difficulty", "stem", "choices", "answer_index",
                                  "explanation", "parameters", "seed"}
    assert len(c["registry"]) == 7
    assert sum(len(t) for t in c["registry"].values()) == 48


def test_fuzz_generation_all_topics_many_seeds():
    """The infinite-bank claim, proven: 48 topics x 15 seeds, all clean."""
    from fs_quiz.schema import make_qid
    import random
    seen = set()
    for domain in registry.list_domains():
        for topic in registry.list_topics(domain):
            fn = registry.get_generator(domain, topic)
            for seed in range(15):
                rng = random.Random(f"{fn.__name__}:{seed}:0")
                q = fn(rng, make_qid(fn.__name__, seed, 0))
                assert q.qid not in seen, f"qid collision: {q.qid}"
                seen.add(q.qid)
                assert validate_question_dict(q.to_dict()) == []
    assert len(seen) == 48 * 15


def test_import_bank_fails_loudly_on_contract_violation(tmp_path):
    bad = str(tmp_path / "bad.json")
    with open(bad, "w") as f:
        json.dump({"schema_version": 1, "questions": []}, f)
    with pytest.raises(ValueError, match="contract validation"):
        QuizEngine().import_bank(bad)
