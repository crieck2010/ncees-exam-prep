"""Versioned question schema — the interop contract for every quiz UI.

Schema v1. Every question is a frozen dataclass, JSON-serializable, with a
stable ``qid`` derived from (generator name, seed, index) so banks are
reproducible. UIs never import generators; they consume ``to_dict()`` JSON.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict

SCHEMA_VERSION = 1

#: The 7 NCEES FS knowledge areas, slugified. Generators register under these.
DOMAINS = (
    "surveying-processes-and-methods",
    "mapping-processes-and-methods",
    "boundary-law-and-real-property",
    "surveying-principles-geodesy",
    "survey-computations",
    "business-concepts-ethics",
    "applied-math-statistics",
)

#: Difficulty bands: 1 = recall/one-step, 2 = multi-step, 3 = exam-hard.
DIFFICULTIES = (1, 2, 3)


def make_qid(generator_name: str, seed: int, index: int) -> str:
    """Stable question id: sha1(generator:seed:index), 12 hex chars."""
    raw = f"{generator_name}:{seed}:{index}".encode()
    return hashlib.sha1(raw).hexdigest()[:12]


@dataclass(frozen=True)
class Question:
    qid: str
    schema_version: int
    domain: str
    topic: str
    difficulty: int
    stem: str
    choices: tuple
    answer_index: int
    explanation: str
    parameters: dict
    seed: int

    def __post_init__(self):
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported schema_version {self.schema_version}")
        if self.domain not in DOMAINS:
            raise ValueError(f"unknown domain {self.domain!r}")
        if self.difficulty not in DIFFICULTIES:
            raise ValueError(f"difficulty must be 1-3, got {self.difficulty}")
        if len(self.choices) != 4:
            raise ValueError("exactly 4 choices required")
        if len(set(self.choices)) != 4:
            raise ValueError(f"choices must be unique: {self.choices}")
        if not 0 <= self.answer_index < 4:
            raise ValueError("answer_index out of range")

    @property
    def correct_choice(self) -> str:
        return self.choices[self.answer_index]

    def grade(self, selected_index: int) -> bool:
        return selected_index == self.answer_index

    def to_dict(self) -> dict:
        d = asdict(self)
        d["choices"] = list(d["choices"])
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict) -> "Question":
        d = dict(d)
        d["choices"] = tuple(d["choices"])
        return cls(**d)

    @classmethod
    def from_json(cls, s: str) -> "Question":
        return cls.from_dict(json.loads(s))
