"""Domain: surveying-processes-and-methods (16-24 FS questions).

7 generators mixing parameterized computations (EDM ppm, three-wire, C&R)
with randomized concept scenarios (error types, GNSS windows, traverse types,
accuracy vs precision). Original content throughout.
"""
from __future__ import annotations

import math

from fs_quiz.generators.survey_computations import _fmt, _mcq
from fs_quiz.registry import register
from fs_quiz.schema import SCHEMA_VERSION, Question

DOMAIN = "surveying-processes-and-methods"


def _mk(rng, qid, topic, difficulty, stem, choices, answer_index,
        explanation, parameters):
    return Question(
        qid=qid, schema_version=SCHEMA_VERSION, domain=DOMAIN, topic=topic,
        difficulty=difficulty, stem=stem, choices=choices,
        answer_index=answer_index, explanation=explanation,
        parameters=parameters, seed=hash(qid) % (2 ** 31),
    )


# ------------------------------------------------------------- error types
_ERROR_KINDS = ["a systematic error", "a random error", "a blunder"]
_ERROR_FACTS = [
    ("The steel tape used for the day's work is later found to be 0.02 ft "
     "too long, affecting every measurement the same way.", 0),
    ("Each angle is read with small, unpredictable pointing variations that "
     "average out over many repetitions.", 1),
    ("A rod reading of 5.42 ft is entered in the field book as 4.52 ft.", 2),
    ("The EDM's ppm correction was never applied, biasing all distances "
     "long on a hot afternoon.", 0),
    ("Level bubbles are centered slightly differently at each setup, with no "
     "consistent direction.", 1),
    ("The wrong backsight point was occupied for an entire traverse leg.", 2),
]


@register(DOMAIN, "error-types")
def gen_error_types(rng, qid):
    facts, kind = rng.choice(_ERROR_FACTS)
    correct = _ERROR_KINDS[kind].capitalize()
    distractors = [k.capitalize() for k in _ERROR_KINDS if k != _ERROR_KINDS[kind]]
    distractors.append("Not an error at all")
    stem = facts + " How is this error classified?"
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = {"a systematic error": "It follows a pattern and biases every measurement the same way \u2014 it can be modeled and corrected.",
            "a random error": "It is unpredictable in sign and magnitude \u2014 it averages down with repetition, never out.",
            "a blunder": "It is a human mistake, unpredictable and often large \u2014 caught by checks and redundancy, not by adjustment."}[_ERROR_KINDS[kind]]
    return _mk(rng, qid, "error-types", 1, stem, choices, ai, expl, {"kind": _ERROR_KINDS[kind]})


# ------------------------------------------------------------- EDM ppm
@register(DOMAIN, "edm-ppm")
def gen_edm_ppm(rng, qid):
    D = rng.uniform(800, 2500)
    # Parameter space is constrained so every pair of choices is separated by
    # > 0.01 ft (provably distinct at 2 decimals): ppm effect in
    # [0.0064, 0.0375], |const| in {0.05, 0.10} with const always negative.
    ppm = rng.choice([8, 12, 15])
    const = rng.choice([-0.10, -0.05])
    ppm_eff = D * ppm / 1e6
    corr = D + ppm_eff + const
    stem = (f"An EDM measures a slope distance of {_fmt(D)} ft. The atmospheric "
            f"correction is {ppm:+d} ppm and the prism constant is {const:+.2f} ft. "
            f"What is the corrected distance?")
    correct = f"{_fmt(corr)} ft"
    distractors = [
        f"{_fmt(D + D * ppm / 100 + const)} ft",  # ppm treated as percent
        f"{_fmt(D - ppm_eff + const)} ft",       # ppm sign flipped
        f"{_fmt(D - ppm_eff - const)} ft",       # both corrections flipped
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Corrected = D(1 + ppm\u00d710\u207b\u2076) + const = {_fmt(D)}"
            f"(1 + {ppm}\u00d710\u207b\u2076) + ({const:+.2f}) = {_fmt(corr)} ft.")
    return _mk(rng, qid, "edm-ppm", 2, stem, choices, ai, expl,
               {"D": D, "ppm": ppm, "const": const})


# ------------------------------------------------------------- three-wire
@register(DOMAIN, "three-wire")
def gen_three_wire(rng, qid):
    upper = rng.uniform(3, 8)
    interval = rng.uniform(0.5, 2.5)
    lower = upper - interval
    middle = (upper + lower) / 2
    stem = (f"Three-wire leveling gives upper {_fmt(upper)} ft and lower "
            f"{_fmt(lower)} ft. What should the middle-wire reading be?")
    correct = f"{_fmt(middle)} ft"
    distractors = [
        f"{_fmt(upper + lower)} ft",      # summed, not averaged
        f"{_fmt(upper - lower)} ft",      # the interval itself
        f"{_fmt((upper + lower) / 4)} ft",
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"The middle wire is the mean of the outer two: "
            f"({_fmt(upper)} + {_fmt(lower)})/2 = {_fmt(middle)} ft. "
            f"A bigger disagreement signals a reading blunder.")
    return _mk(rng, qid, "three-wire", 1, stem, choices, ai, expl,
               {"upper": upper, "lower": lower})


# ------------------------------------------------------------- curvature & refraction
@register(DOMAIN, "curvature-refraction")
def gen_cr(rng, qid):
    miles = rng.uniform(0.1, 0.6)
    corr = 0.574 * miles ** 2  # combined C&R, feet; miles input
    stem = (f"A level sight is {_fmt(miles, 2)} miles long. What is the "
            f"combined curvature-and-refraction correction?")
    correct = f"{_fmt(corr, 3)} ft"
    distractors = [
        f"{_fmt(0.667 * miles ** 2, 3)} ft",  # curvature only, no refraction
        f"{_fmt(corr * 10, 3)} ft",           # decimal slip
        f"{_fmt(0.574 * miles, 3)} ft",       # forgot to square
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Combined C&R \u2248 0.574 ft per mile\u00b2 (curvature 0.667 minus "
            f"refraction). 0.574 \u00d7 {_fmt(miles, 2)}\u00b2 = {_fmt(corr, 3)} ft. "
            f"Balance your sights and it cancels.")
    return _mk(rng, qid, "curvature-refraction", 2, stem, choices, ai, expl,
               {"miles": miles})


# ------------------------------------------------------------- GNSS window
@register(DOMAIN, "gnss-window")
def gen_gnss(rng, qid):
    labels = ["A", "B", "C"]
    pdops = sorted(rng.sample([round(rng.uniform(1.2, 6.0), 1) for _ in range(6)], 3))
    sats = [rng.randint(6, 12) for _ in range(3)]
    # best = lowest PDOP; break ties with more satellites
    order = sorted(range(3), key=lambda i: (pdops[i], -sats[i]))
    best = labels[order[0]]
    # shuffle presentation order
    presented = list(zip(labels, pdops, sats))
    rng.shuffle(presented)
    desc = "; ".join(f"Window {l}: PDOP {p}, {s} satellites" for l, p, s in presented)
    stem = (f"Three candidate RTK observation windows: {desc}. "
            f"Which window should the crew choose?")
    correct = f"Window {best}"
    distractors = [f"Window {l}" for l in labels if l != best] + ["It makes no difference"]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = (f"Lower PDOP = stronger satellite geometry. Window {best} has the "
            f"lowest PDOP ({pdops[order[0]]}); satellite count breaks ties. "
            f"High PDOP amplifies every ranging error.")
    return _mk(rng, qid, "gnss-window", 2, stem, choices, ai, expl,
               {"best": best})


# ------------------------------------------------------------- traverse types
_TRAVERSE_FACTS = [
    ("begins at control point CP1 and closes back on CP1", "A closed loop traverse"),
    ("begins at CP1 and ends at a different known control point, CP9",
     "A closed (connecting/link) traverse"),
    ("begins at CP1 and ends at an unknown point with no check",
     "An open traverse"),
]
_TRAVERSE_CHOICES = ["A closed loop traverse", "A closed (connecting/link) traverse",
                     "An open traverse", "An azimuth traverse"]


@register(DOMAIN, "traverse-types")
def gen_traverse_types(rng, qid):
    facts, correct = rng.choice(_TRAVERSE_FACTS)
    stem = f"A traverse {facts}. How is this traverse classified?"
    distractors = [c for c in _TRAVERSE_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = {"A closed loop traverse": "It starts and ends at the same known point \u2014 angles and position both check.",
            "A closed (connecting/link) traverse": "It connects two known control points \u2014 the strongest geometry, both ends checked.",
            "An open traverse": "It ends blind with no check \u2014 errors accumulate unseen; avoid for control."}[correct]
    return _mk(rng, qid, "traverse-types", 1, stem, choices, ai, expl,
               {"correct": correct})


# ------------------------------------------------------------- accuracy vs precision
_AP_FACTS = [
    ("tightly clustered 0.30 ft north of the true position",
     "Precise but not accurate"),
    ("centered on the true position but scattered \u00b10.50 ft",
     "Accurate but not precise"),
    ("tightly clustered on the true position", "Accurate and precise"),
    ("scattered \u00b10.80 ft with a 0.40-ft north bias", "Neither accurate nor precise"),
]
_AP_CHOICES = ["Accurate and precise", "Precise but not accurate",
               "Accurate but not precise", "Neither accurate nor precise"]


@register(DOMAIN, "accuracy-precision")
def gen_acc_prec(rng, qid):
    facts, correct = rng.choice(_AP_FACTS)
    stem = (f"Repeated measurements of a known baseline come out {facts}. "
            f"How are these measurements described?")
    distractors = [c for c in _AP_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = ("Accuracy = closeness to truth (bias); precision = repeatability "
            "(scatter). A tight cluster off the mark is precise but biased \u2014 "
            "the classic signature of uncorrected systematic error.")
    return _mk(rng, qid, "accuracy-precision", 1, stem, choices, ai, expl,
               {"correct": correct})
