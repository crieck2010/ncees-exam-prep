"""QuizEngine: deterministic generation, bank import/export, grading.

The engine never touches the network or the UI. It turns (domain, topic, n,
seed) into reproducible question banks serialized as versioned JSON — the
artifact every quiz UI consumes.
"""
from __future__ import annotations

import json
import random

from fs_quiz import registry
from fs_quiz.schema import SCHEMA_VERSION, Question

# Import generator modules so they self-register. New domains add one import.
from fs_quiz.generators import applied_math  # noqa: F401
from fs_quiz.generators import boundary_law  # noqa: F401
from fs_quiz.generators import business_ethics  # noqa: F401
from fs_quiz.generators import geodesy  # noqa: F401
from fs_quiz.generators import mapping_processes  # noqa: F401
from fs_quiz.generators import survey_computations  # noqa: F401
from fs_quiz.generators import surveying_processes  # noqa: F401


class QuizEngine:
    def generate(self, domain: str, topic: str, n: int = 10, seed: int = 0) -> list:
        """Generate n questions; identical (domain, topic, n, seed) replays exactly."""
        from fs_quiz.schema import make_qid
        gen = registry.get_generator(domain, topic)
        questions = []
        for i in range(n):
            rng = random.Random(f"{gen.__name__}:{seed}:{i}")
            qid = make_qid(gen.__name__, seed, i)
            questions.append(gen(rng, qid))
        return questions

    def generate_bank(self, spec: dict | None = None, n_per_topic: int = 10,
                      seed: int = 0) -> list:
        """Generate a mixed bank. spec: {domain: [topics]}; None = everything."""
        if spec is None:
            spec = registry.registry_snapshot()
        bank = []
        for di, (domain, topics) in enumerate(sorted(spec.items())):
            for ti, topic in enumerate(topics):
                bank.extend(
                    self.generate(domain, topic, n=n_per_topic,
                                  seed=seed + di * 1000 + ti)
                )
        return bank

    # -- serialization -----------------------------------------------------
    def export_bank(self, questions: list, path: str) -> str:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "generator": "fs-exam-prep",
            "engine_version": "1.0.0",
            "question_count": len(questions),
            "questions": [q.to_dict() for q in questions],
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=1, sort_keys=True)
        return path

    def import_bank(self, path: str) -> list:
        from fs_quiz.contract import validate_bank_dict
        with open(path) as f:
            payload = json.load(f)
        errors = validate_bank_dict(payload)
        if errors:
            raise ValueError(
                "bank failed v1 contract validation:\n" + "\n".join(errors[:10])
                + (f"\n... and {len(errors) - 10} more" if len(errors) > 10 else "")
            )
        return [Question.from_dict(q) for q in payload["questions"]]

    # -- grading ------------------------------------------------------------
    def grade(self, questions: list, answers: dict) -> dict:
        """answers: {qid: selected_index}. Returns per-question + summary."""
        results = []
        for q in questions:
            sel = answers.get(q.qid)
            results.append({
                "qid": q.qid,
                "domain": q.domain,
                "topic": q.topic,
                "selected": sel,
                "correct": q.answer_index,
                "is_correct": sel is not None and q.grade(sel),
            })
        correct = sum(r["is_correct"] for r in results)
        return {
            "total": len(results),
            "correct": correct,
            "score_pct": round(100 * correct / len(results), 1) if results else 0.0,
            "results": results,
        }
