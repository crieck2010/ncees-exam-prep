"""Domain generator modules. Each module registers its topics on import."""
from fs_quiz.generators import applied_math  # noqa: F401
from fs_quiz.generators import boundary_law  # noqa: F401
from fs_quiz.generators import business_ethics  # noqa: F401
from fs_quiz.generators import geodesy  # noqa: F401
from fs_quiz.generators import mapping_processes  # noqa: F401
from fs_quiz.generators import survey_computations  # noqa: F401
from fs_quiz.generators import surveying_processes  # noqa: F401

__all__ = [
    "applied_math",
    "boundary_law",
    "business_ethics",
    "geodesy",
    "mapping_processes",
    "survey_computations",
    "surveying_processes",
]
