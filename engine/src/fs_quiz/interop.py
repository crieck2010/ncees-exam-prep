"""Duck-typed bridges to sibling systems. This package never imports a
sibling — every bridge works on plain dicts/lists so install graphs stay
acyclic and every bridge is testable offline (same convention as the
survey-suite engines' interop.py modules).
"""

from fs_quiz import registry
from fs_quiz.schema import SCHEMA_VERSION


def flutter_contract() -> dict:
    """The JSON contract the Flutter quiz app implements against.

    The app never imports this package: it reads exported bank JSON files
    (see QuizEngine.export_bank) whose shape is fully described here.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "bank_file": {
            "schema_version": "int, must equal engine SCHEMA_VERSION",
            "generator": "str, e.g. 'fs-exam-prep'",
            "engine_version": "str, semver of the engine that generated it",
            "question_count": "int",
            "questions": ["array of question objects (see below)"],
        },
        "question": {
            "qid": "str, stable 12-hex id",
            "schema_version": "int",
            "domain": "str, one of the 7 FS knowledge-area slugs",
            "topic": "str, generator topic slug",
            "difficulty": "int 1-3",
            "stem": "str, question text (plain text, no HTML)",
            "choices": "array of 4 unique strings",
            "answer_index": "int 0-3",
            "explanation": "str, worked solution with the question's numbers",
            "parameters": "object, the randomized inputs (for re-derivation)",
            "seed": "int, master seed used",
        },
        "grading": "client-side: selected_index == answer_index",
        "registry": registry.registry_snapshot(),
    }


def to_jsonl(questions: list, path: str) -> str:
    """One question per line — convenient for streaming into mobile bundles."""
    with open(path, "w") as f:
        for q in questions:
            f.write(q.to_json() + "\n")
    return path


def from_jsonl(path: str) -> list:
    from fs_quiz.schema import Question
    with open(path) as f:
        return [Question.from_json(line) for line in f if line.strip()]
