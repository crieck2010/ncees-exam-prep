"""fs-exam-prep: parameterized FS exam question-bank engine.

Engine core is stdlib-only. UI layers (CLI, Streamlit, Flutter) consume
versioned JSON question banks produced by :class:`QuizEngine`.
"""

from fs_quiz.schema import Question, SCHEMA_VERSION, DOMAINS, make_qid
from fs_quiz.registry import register, list_domains, list_topics, get_generator
from fs_quiz.engine import QuizEngine

__all__ = [
    "Question",
    "SCHEMA_VERSION",
    "DOMAINS",
    "make_qid",
    "register",
    "list_domains",
    "list_topics",
    "get_generator",
    "QuizEngine",
]

__version__ = "1.0.0"
