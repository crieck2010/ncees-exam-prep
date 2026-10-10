"""v1 contract enforcement: machine-checked guarantees for schema v1.

The JSON Schema file at ``schema/question-v1.json`` is the canonical,
language-agnostic contract. This module implements the same checks in
stdlib-only Python (the engine core takes no dependencies), and
:func:`validate_bank_dict` is the single gate used by ``import_bank``,
the ``fs-quiz validate`` command, and the golden-file tests.

Contract guarantees (see docs/SCHEMA_CONTRACT.md):
- v1 fields are never removed or renamed; additive changes are minor-only.
- Any breaking change ships as schema_version 2 with a migration guide.
"""
from __future__ import annotations

from fs_quiz.schema import DOMAINS, SCHEMA_VERSION

REQUIRED_QUESTION_FIELDS = (
    "qid", "schema_version", "domain", "topic", "difficulty",
    "stem", "choices", "answer_index", "explanation", "parameters", "seed",
)

REQUIRED_BANK_FIELDS = (
    "schema_version", "generator", "engine_version",
    "question_count", "questions",
)


def validate_question_dict(d: dict, where: str = "question") -> list:
    """Return a list of contract violations (empty = valid)."""
    errors = []
    if not isinstance(d, dict):
        return [f"{where}: not an object"]
    for f in REQUIRED_QUESTION_FIELDS:
        if f not in d:
            errors.append(f"{where}: missing field {f!r}")
    if errors:
        return errors
    if d["schema_version"] != SCHEMA_VERSION:
        errors.append(f"{where}: schema_version {d['schema_version']!r} != {SCHEMA_VERSION}")
    if d["domain"] not in DOMAINS:
        errors.append(f"{where}: unknown domain {d['domain']!r}")
    if d["difficulty"] not in (1, 2, 3):
        errors.append(f"{where}: difficulty must be 1-3, got {d['difficulty']!r}")
    if not isinstance(d["stem"], str) or not d["stem"].strip():
        errors.append(f"{where}: stem must be a non-empty string")
    ch = d["choices"]
    if not isinstance(ch, list) or len(ch) != 4:
        errors.append(f"{where}: choices must be a list of 4 strings")
    elif not all(isinstance(c, str) and c.strip() for c in ch):
        errors.append(f"{where}: choices must be non-empty strings")
    elif len(set(ch)) != 4:
        errors.append(f"{where}: choices must be unique")
    ai = d["answer_index"]
    if not isinstance(ai, int) or isinstance(ai, bool) or not 0 <= ai < 4:
        errors.append(f"{where}: answer_index must be int 0-3")
    if not isinstance(d["explanation"], str) or not d["explanation"].strip():
        errors.append(f"{where}: explanation must be a non-empty string")
    if not isinstance(d["parameters"], dict):
        errors.append(f"{where}: parameters must be an object")
    if not isinstance(d["qid"], str) or not d["qid"]:
        errors.append(f"{where}: qid must be a non-empty string")
    return errors


def validate_bank_dict(payload: dict) -> list:
    """Return a list of contract violations for a whole bank file."""
    errors = []
    if not isinstance(payload, dict):
        return ["bank: not an object"]
    for f in REQUIRED_BANK_FIELDS:
        if f not in payload:
            errors.append(f"bank: missing field {f!r}")
    if errors:
        return errors
    if payload["schema_version"] != SCHEMA_VERSION:
        errors.append(
            f"bank: schema_version {payload['schema_version']!r} != {SCHEMA_VERSION}")
    questions = payload["questions"]
    if not isinstance(questions, list):
        return errors + ["bank: questions must be a list"]
    if payload["question_count"] != len(questions):
        errors.append(
            f"bank: question_count {payload['question_count']} != len(questions) {len(questions)}")
    seen = set()
    for i, q in enumerate(questions):
        errors.extend(validate_question_dict(q, where=f"questions[{i}]"))
        qid = q.get("qid") if isinstance(q, dict) else None
        if qid in seen:
            errors.append(f"questions[{i}]: duplicate qid {qid!r}")
        seen.add(qid)
    return errors
