"""Domain: applied-math-statistics (10-15 FS questions).

6 generators: law of sines, law of cosines, standard error of the mean,
confidence intervals, significant figures, unit conversions.
"""
from __future__ import annotations

import math

from fs_quiz.generators.survey_computations import _fmt, _mcq
from fs_quiz.registry import register
from fs_quiz.schema import SCHEMA_VERSION, Question

DOMAIN = "applied-math-statistics"


def _mk(rng, qid, topic, difficulty, stem, choices, answer_index,
        explanation, parameters):
    return Question(
        qid=qid, schema_version=SCHEMA_VERSION, domain=DOMAIN, topic=topic,
        difficulty=difficulty, stem=stem, choices=choices,
        answer_index=answer_index, explanation=explanation,
        parameters=parameters, seed=hash(qid) % (2 ** 31),
    )


# ------------------------------------------------------------- law of sines
@register(DOMAIN, "law-of-sines")
def gen_los(rng, qid):
    A = rng.uniform(35, 70)
    B = rng.uniform(50, 90)
    if A + B >= 150:
        B = 150 - A - rng.uniform(5, 20)
    a = rng.uniform(150, 500)
    b = a * math.sin(math.radians(B)) / math.sin(math.radians(A))
    stem = (f"In triangle ABC, angle A = {_fmt(A)}\u00b0, angle B = {_fmt(B)}\u00b0, "
            f"and side a = {_fmt(a)} ft. What is the length of side b?")
    correct = f"{_fmt(b)} ft"
    distractors = [
        f"{_fmt(a * math.sin(math.radians(A)) / math.sin(math.radians(B)))} ft",  # inverted ratio
        f"{_fmt(a + b - a)} ft",  # placeholder replaced below
        f"{_fmt(180 - A - B)} ft",  # angle reported as length
    ]
    distractors[1] = f"{_fmt(a * math.cos(math.radians(B)) / math.cos(math.radians(A)))} ft"
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"b / sin B = a / sin A \u2192 b = {_fmt(a)} \u00d7 sin({_fmt(B)}\u00b0) / "
            f"sin({_fmt(A)}\u00b0) = {_fmt(b)} ft.")
    return _mk(rng, qid, "law-of-sines", 2, stem, choices, ai, expl,
               {"A": A, "B": B, "a": a})


# ------------------------------------------------------------- law of cosines
@register(DOMAIN, "law-of-cosines")
def gen_loc(rng, qid):
    a = rng.uniform(150, 400)
    b = rng.uniform(150, 400)
    C = rng.uniform(40, 110)
    Cr = math.radians(C)
    c = math.sqrt(a ** 2 + b ** 2 - 2 * a * b * math.cos(Cr))
    stem = (f"In triangle ABC, side a = {_fmt(a)} ft, side b = {_fmt(b)} ft, and "
            f"the included angle C = {_fmt(C)}\u00b0. What is the length of side c?")
    correct = f"{_fmt(c)} ft"
    distractors = [
        f"{_fmt(a ** 2 + b ** 2 - 2 * a * b * math.cos(Cr))} ft",  # forgot sqrt
        f"{_fmt(math.sqrt(a ** 2 + b ** 2 + 2 * a * b * math.cos(Cr)))} ft",  # wrong sign
        f"{_fmt(a + b)} ft",  # triangle inequality ignored
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"c\u00b2 = a\u00b2 + b\u00b2 \u2212 2ab\u00b7cos C = {_fmt(a)}\u00b2 + {_fmt(b)}\u00b2 "
            f"\u2212 2({_fmt(a)})({_fmt(b)})cos({_fmt(C)}\u00b0); c = {_fmt(c)} ft.")
    return _mk(rng, qid, "law-of-cosines", 2, stem, choices, ai, expl,
               {"a": a, "b": b, "C": C})


# ------------------------------------------------------------- standard error of the mean
@register(DOMAIN, "std-error-mean")
def gen_sem(rng, qid):
    s = rng.uniform(0.02, 0.12)
    n = rng.choice([4, 9, 16, 25])
    sem = s / math.sqrt(n)
    stem = (f"Repeated measurements have a standard deviation of {_fmt(s, 3)} ft. "
            f"What is the standard error of the mean of {n} measurements?")
    correct = f"{_fmt(sem, 4)} ft"
    distractors = [
        f"{_fmt(s * math.sqrt(n), 4)} ft",  # multiplied by sqrt(n)
        f"{_fmt(s / n, 4)} ft",             # divided by n, not sqrt(n)
        f"{_fmt(s, 3)} ft",                 # reported s unchanged
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"SE(mean) = s / \u221an = {_fmt(s, 3)} / \u221a{n} = {_fmt(sem, 4)} ft. "
            f"Averaging n independent measurements tightens precision by \u221an.")
    return _mk(rng, qid, "std-error-mean", 2, stem, choices, ai, expl,
               {"s": s, "n": n})


# ------------------------------------------------------------- confidence intervals
_CONF = {1: "68%", 2: "95%", 3: "99.7%"}


@register(DOMAIN, "confidence-intervals")
def gen_conf(rng, qid):
    k = rng.choice([1, 2, 3])
    sigma = rng.uniform(0.02, 0.10)
    stem = (f"Measurement errors are normally distributed with standard deviation "
            f"\u03c3 = {_fmt(sigma, 3)} ft. About what percentage of measurements "
            f"fall within \u00b1{_fmt(k * sigma, 3)} ft of the mean?")
    correct = _CONF[k]
    distractors = [v for kk, v in _CONF.items() if kk != k] + ["50%"]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = (f"\u00b1{_fmt(k * sigma, 3)} ft is \u00b1{k}\u03c3. The 68\u201395\u201399.7 rule: "
            f"\u00b11\u03c3 \u2192 68%, \u00b12\u03c3 \u2192 95%, \u00b13\u03c3 \u2192 99.7%.")
    return _mk(rng, qid, "confidence-intervals", 1, stem, choices, ai, expl,
               {"k": k, "sigma": sigma})


# ------------------------------------------------------------- significant figures
_SIGFIGS = [("0.00450", 3), ("100.0", 4), ("8.020", 4), ("0.0100", 3),
            ("2500.", 4), ("0.0007060", 4), ("93.10", 4)]


@register(DOMAIN, "significant-figures")
def gen_sigfigs(rng, qid):
    number, count = rng.choice(_SIGFIGS)
    stem = f"How many significant figures are in {number}?"
    correct = f"{count}"
    cand = [f"{count - 1}", f"{count + 1}", f"{count + 2}"]
    distractors = [c for c in cand if int(c) >= 1][:3]
    while len(distractors) < 3:
        extra = f"{count + 3}"
        if extra not in distractors:
            distractors.append(extra)
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"In {number}: leading zeros are never significant; captive zeros "
            f"are; trailing zeros are significant only with a decimal point. "
            f"Count = {count}.")
    return _mk(rng, qid, "significant-figures", 1, stem, choices, ai, expl,
               {"number": number, "count": count})


# ------------------------------------------------------------- unit conversions
@register(DOMAIN, "unit-conversions")
def gen_units(rng, qid):
    if rng.random() < 0.5:
        sqft = rng.uniform(50000, 500000)
        acres = sqft / 43560
        stem = f"A parcel measures {_fmt(sqft, 0)} square feet. What is its area in acres?"
        correct = f"{_fmt(acres)} acres"
        distractors = [f"{_fmt(sqft * 43560, 0)} acres", f"{_fmt(sqft / 43560 / 2)} acres",
                       f"{_fmt(acres * 2)} acres"]
        expl = f"{_fmt(sqft, 0)} / 43,560 = {_fmt(acres)} acres."
        params = {"kind": "sqft-to-acres", "sqft": sqft}
    else:
        ft = rng.uniform(500, 5000)
        m = ft * 0.3048
        stem = f"A distance of {_fmt(ft)} ft is equivalent to how many meters?"
        correct = f"{_fmt(m)} m"
        distractors = [f"{_fmt(ft / 0.3048)} m", f"{_fmt(ft * 0.0328084)} m",
                       f"{_fmt(m / 2)} m"]
        expl = f"{_fmt(ft)} \u00d7 0.3048 = {_fmt(m)} m."
        params = {"kind": "ft-to-m", "ft": ft}
    choices, ai = _mcq(rng, correct, distractors)
    return _mk(rng, qid, "unit-conversions", 1, stem, choices, ai, expl, params)
