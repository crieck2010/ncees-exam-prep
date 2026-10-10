"""Domain: surveying-principles-geodesy (13-20 FS questions).

5 generators: orthometric heights, combined factor, elevation factor formula,
datums, grid vs ground. Original content throughout.
"""
from __future__ import annotations

from fs_quiz.generators.survey_computations import _fmt, _mcq
from fs_quiz.registry import register
from fs_quiz.schema import SCHEMA_VERSION, Question

DOMAIN = "surveying-principles-geodesy"


def _mk(rng, qid, topic, difficulty, stem, choices, answer_index,
        explanation, parameters):
    return Question(
        qid=qid, schema_version=SCHEMA_VERSION, domain=DOMAIN, topic=topic,
        difficulty=difficulty, stem=stem, choices=choices,
        answer_index=answer_index, explanation=explanation,
        parameters=parameters, seed=hash(qid) % (2 ** 31),
    )


# ------------------------------------------------------------- orthometric height
@register(DOMAIN, "orthometric-height")
def gen_ortho(rng, qid):
    h = rng.uniform(300, 900)          # ellipsoid height, ft
    N = rng.uniform(-30, 10)           # geoid height, ft
    H = h - N
    stem = (f"GNSS gives an ellipsoid height of {_fmt(h)} ft at a point where "
            f"the geoid height is {_fmt(N)} ft. What is the orthometric height?")
    correct = f"{_fmt(H)} ft"
    distractors = [
        f"{_fmt(h + N)} ft",   # added instead of subtracted
        f"{_fmt(N - h)} ft",   # reversed
        f"{_fmt(h)} ft",       # ellipsoid height reported as-is
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"H = h \u2212 N = {_fmt(h)} \u2212 ({_fmt(N)}) = {_fmt(H)} ft. "
            f"Orthometric heights (elevations) are measured from the geoid.")
    return _mk(rng, qid, "orthometric-height", 2, stem, choices, ai, expl,
               {"h": h, "N": N})


# ------------------------------------------------------------- combined factor
@register(DOMAIN, "combined-factor")
def gen_combined(rng, qid):
    ground = rng.uniform(2000, 12000)
    cf = rng.uniform(0.9997, 1.0002)
    grid = ground * cf
    stem = (f"A ground distance of {_fmt(ground)} ft is reduced to grid with a "
            f"combined factor of {_fmt(cf, 5)}. What is the grid distance?")
    correct = f"{_fmt(grid)} ft"
    distractors = [
        f"{_fmt(ground / cf)} ft",          # divided instead of multiplied
        f"{_fmt(ground)} ft",               # factor forgotten
        f"{_fmt(ground * cf ** 2)} ft",     # factor applied twice
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Grid = ground \u00d7 combined factor = {_fmt(ground)} \u00d7 "
            f"{_fmt(cf, 5)} = {_fmt(grid)} ft. (Combined = scale factor \u00d7 "
            f"elevation factor.)")
    return _mk(rng, qid, "combined-factor", 2, stem, choices, ai, expl,
               {"ground": ground, "cf": cf})


# ------------------------------------------------------------- elevation factor formula
_EF_CHOICES = ["EF = R / (R + h)", "EF = R / (R \u2212 h)",
               "EF = h / R", "EF = 1 + h / R"]


@register(DOMAIN, "elevation-factor")
def gen_ef(rng, qid):
    h = rng.randint(1000, 9000)
    stem = (f"At a project with a mean ellipsoid height of {_fmt(h, 0)} ft, which "
            f"formula gives the elevation factor (R = mean earth radius)?")
    correct = _EF_CHOICES[0]
    distractors = _EF_CHOICES[1:]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"EF = R/(R+h) \u2014 always slightly less than 1 above the ellipsoid, "
            f"shrinking ground distances to the ellipsoid surface. At "
            f"{_fmt(h, 0)} ft the factor is about {_fmt(20906000 / (20906000 + h), 7)}.")
    return _mk(rng, qid, "elevation-factor", 2, stem, choices, ai, expl,
               {"h": h, "correct": correct})


# ------------------------------------------------------------- datums
_DATUM_FACTS = [
    ("Horizontal positions on a new county control network (latitude/longitude)",
     "NAD83"),
    ("Orthometric heights (elevations) on an NGS data sheet", "NAVD88"),
    ("Ellipsoid heights coming straight off a GNSS receiver", "NAD83 (GRS80 ellipsoid)"),
]
_DATUM_CHOICES = ["NAD83", "NAVD88", "NGVD29", "WGS84"]


@register(DOMAIN, "datums")
def gen_datums(rng, qid):
    facts, correct = rng.choice(_DATUM_FACTS)
    stem = f"{facts} are referenced to which datum?"
    distractors = [c for c in _DATUM_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = ("NAD83 = current US horizontal datum (GRS80 ellipsoid, so GNSS "
            "ellipsoid heights live in it). NAVD88 = current US vertical datum "
            "for orthometric heights. NGVD29 is superseded; WGS84 is the GNSS "
            "broadcast datum, not the US mapping datum.")
    return _mk(rng, qid, "datums", 1, stem, choices, ai, expl,
               {"correct": correct})


# ------------------------------------------------------------- grid vs ground sense
@register(DOMAIN, "grid-vs-ground")
def gen_grid_ground(rng, qid):
    cf = rng.choice([0.99985, 0.99993, 1.00008, 1.00012])
    stem = (f"A project has a combined factor of {_fmt(cf, 5)}. For a given "
            f"line, how does the grid distance compare to the ground distance?")
    correct = ("The grid distance is shorter" if cf < 1
               else "The grid distance is longer")
    distractors = [
        "The grid distance is longer" if cf < 1 else "The grid distance is shorter",
        "They are exactly equal",
        "It cannot be determined from the factor",
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Grid = ground \u00d7 {_fmt(cf, 5)}. A factor below 1 shrinks the "
            f"distance (high elevations / inside the projection); above 1 "
            f"stretches it. Always reduce measurements before comparing to "
            f"State Plane coordinates.")
    return _mk(rng, qid, "grid-vs-ground", 1, stem, choices, ai, expl,
               {"cf": cf})
