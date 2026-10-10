"""Phase 1 domain: survey-computations (17-26 FS questions, second-heaviest area).

12 parameterized generators. Each takes ``(rng, qid)`` and returns a Question.
All questions are original; every distractor is a classic exam mistake
(wrong quadrant, swapped sin/cos, forgotten 1/2, ...), so wrong answers teach.

Conventions:
- Distances in feet, coordinates in feet, angles in degrees unless stated.
- ``_mcq`` builds 4 unique choices and locates the correct one.
- Explanations show the worked solution with the question's own numbers.
"""
from __future__ import annotations

import math

from fs_quiz.registry import register
from fs_quiz.schema import SCHEMA_VERSION, Question

DOMAIN = "survey-computations"


def _fmt(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}"


def _mcq(rng, correct: str, distractors: list) -> tuple:
    """Return (choices tuple, answer_index) with 4 unique choices, shuffled."""
    pool = [correct]
    for d in distractors:
        if d not in pool:
            pool.append(d)
    if len(pool) < 4:
        raise ValueError(f"need 4 unique choices, got {pool}")
    rng.shuffle(pool)
    return tuple(pool[:4]), pool.index(correct)


def _mk(rng, qid, topic, difficulty, stem, choices, answer_index,
        explanation, parameters, seed_tag=""):
    return Question(
        qid=qid,
        schema_version=SCHEMA_VERSION,
        domain=DOMAIN,
        topic=topic,
        difficulty=difficulty,
        stem=stem,
        choices=choices,
        answer_index=answer_index,
        explanation=explanation,
        parameters=parameters,
        seed=hash((qid, seed_tag)) % (2 ** 31),
    )


def _bearing_str(az: float) -> str:
    az %= 360.0
    if az < 90:
        q, a = "N", f"N {_fmt(az)} E"
    elif az < 180:
        a = f"S {_fmt(180 - az)} E"
    elif az < 270:
        a = f"S {_fmt(az - 180)} W"
    else:
        a = f"N {_fmt(360 - az)} W"
    return a


# ---------------------------------------------------------------- inverse
@register(DOMAIN, "inverse")
def gen_inverse(rng, qid):
    n1 = rng.uniform(1000, 9000)
    e1 = rng.uniform(1000, 9000)
    d_n = rng.uniform(-800, 800)
    d_e = rng.uniform(-800, 800)
    if abs(d_n) < 50:
        d_n = 250.0
    if abs(d_e) < 50:
        d_e = -180.0
    dist = math.hypot(d_n, d_e)
    az = math.degrees(math.atan2(d_e, d_n)) % 360.0

    stem = (f"Point A is at N {_fmt(n1)}, E {_fmt(e1)}. Point B is at "
            f"N {_fmt(n1 + d_n)}, E {_fmt(e1 + d_e)}. "
            f"What is the azimuth from A to B?")
    correct = f"{_fmt(az)}\u00b0"
    distractors = [
        f"{_fmt((az + 180) % 360)}\u00b0",   # back azimuth
        f"{_fmt((360 - az) % 360)}\u00b0",   # mirrored quadrant
        f"{_fmt((180 - az) % 360)}\u00b0",   # wrong quadrant correction
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"\u0394N = {_fmt(d_n)} ft, \u0394E = {_fmt(d_e)} ft. "
            f"Distance = \u221a(\u0394N\u00b2 + \u0394E\u00b2) = {_fmt(dist)} ft. "
            f"Azimuth = atan2(\u0394E, \u0394N) = {_fmt(az)}\u00b0 "
            f"({_bearing_str(az)}). atan2 handles the quadrant automatically.")
    return _mk(rng, qid, "inverse", 1, stem, choices, ai, expl,
               {"N1": n1, "E1": e1, "N2": n1 + d_n, "E2": e1 + d_e})


# ---------------------------------------------------------------- forward
@register(DOMAIN, "forward")
def gen_forward(rng, qid):
    n1 = rng.uniform(1000, 9000)
    e1 = rng.uniform(1000, 9000)
    az = rng.uniform(0, 360)
    dist = rng.uniform(100, 1200)
    azr = math.radians(az)
    n2 = n1 + dist * math.cos(azr)
    e2 = e1 + dist * math.sin(azr)

    stem = (f"From point A at N {_fmt(n1)}, E {_fmt(e1)}, a line runs "
            f"{_fmt(dist)} ft on azimuth {_fmt(az)}\u00b0. "
            f"What is the northing of point B?")
    correct = f"{_fmt(n2)} ft"
    distractors = [
        f"{_fmt(n1 + dist * math.sin(azr))} ft",  # sin/cos swapped
        f"{_fmt(e2)} ft",                          # easting instead of northing
        f"{_fmt(n1 - dist * math.cos(azr))} ft",  # sign error
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"N2 = N1 + D\u00b7cos(az) = {_fmt(n1)} + {_fmt(dist)}\u00b7cos({_fmt(az)}\u00b0) "
            f"= {_fmt(n2)} ft. (Easting would use sine.)")
    return _mk(rng, qid, "forward", 1, stem, choices, ai, expl,
               {"N1": n1, "E1": e1, "az": az, "dist": dist})


# ------------------------------------------------------- traverse misclosure
@register(DOMAIN, "traverse-misclosure")
def gen_misclosure(rng, qid):
    ex = rng.uniform(0.04, 0.30) * rng.choice([1, -1])
    ey = rng.uniform(0.04, 0.30) * rng.choice([1, -1])
    perim = rng.uniform(1500, 6000)
    e = math.hypot(ex, ey)
    ratio = perim / e

    stem = (f"A closed loop traverse has latitudes summing to {_fmt(ex)} ft and "
            f"departures summing to {_fmt(ey)} ft. The traverse perimeter is "
            f"{_fmt(perim, 0)} ft. What is the linear error of closure and the "
            f"relative precision?")
    correct = f"{_fmt(e)} ft; 1:{ratio:,.0f}"
    distractors = [
        f"{_fmt(abs(ex) + abs(ey))} ft; 1:{perim / (abs(ex) + abs(ey)):,.0f}",  # summed, not RSS
        f"{_fmt(e)} ft; 1:{e / perim:,.4f}",    # inverted ratio
        f"{_fmt(max(abs(ex), abs(ey)))} ft; 1:{perim / max(abs(ex), abs(ey)):,.0f}",
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"e = \u221a(\u03a3lat\u00b2 + \u03a3dep\u00b2) = "
            f"\u221a({_fmt(ex)}\u00b2 + {_fmt(ey)}\u00b2) = {_fmt(e)} ft. "
            f"Precision = e / perimeter = 1:{ratio:,.0f}.")
    return _mk(rng, qid, "traverse-misclosure", 2, stem, choices, ai, expl,
               {"sum_lat": ex, "sum_dep": ey, "perimeter": perim})


# ---------------------------------------------------------------- bowditch
@register(DOMAIN, "bowditch")
def gen_bowditch(rng, qid):
    err_lat = rng.uniform(0.05, 0.40) * rng.choice([1, -1])
    err_dep = rng.uniform(0.05, 0.40) * rng.choice([1, -1])
    perim = rng.uniform(2000, 8000)
    leg = rng.uniform(200, 900)
    corr_lat = -err_lat * leg / perim
    corr_dep = -err_dep * leg / perim

    which = rng.choice(["latitude", "departure"])
    corr = corr_lat if which == "latitude" else corr_dep
    err = err_lat if which == "latitude" else err_dep
    stem = (f"A traverse miscloses by {_fmt(err_lat)} ft in latitude and "
            f"{_fmt(err_dep)} ft in departure over a {_fmt(perim, 0)}-ft perimeter. "
            f"Using the compass (Bowditch) rule, what is the {which} correction "
            f"for a {_fmt(leg, 0)}-ft leg?")
    correct = f"{_fmt(corr)} ft"
    distractors = [
        f"{_fmt(-corr)} ft",                                   # sign error
        f"{_fmt(-err * perim / leg)} ft",                      # inverted proportion
        f"{_fmt(-err)} ft",                                   # full error dumped on one leg
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Bowditch: correction = \u2212(error \u00d7 leg / perimeter) = "
            f"\u2212({_fmt(err)} \u00d7 {_fmt(leg, 0)} / {_fmt(perim, 0)}) = "
            f"{_fmt(corr)} ft. Corrections oppose the misclosure and scale with leg length.")
    return _mk(rng, qid, "bowditch", 2, stem, choices, ai, expl,
               {"err_lat": err_lat, "err_dep": err_dep,
                "perimeter": perim, "leg": leg})


# ------------------------------------------------------------- area by coords
@register(DOMAIN, "area-coordinates")
def gen_area(rng, qid):
    w = rng.uniform(150, 600)
    h = rng.uniform(150, 600)
    n0, e0 = rng.uniform(1000, 5000), rng.uniform(1000, 5000)
    pts = [(e0, n0), (e0 + w, n0), (e0 + w, n0 + h), (e0, n0 + h)]
    s = sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1]
            for i in range(4))
    area_sf = abs(s) / 2
    acres = area_sf / 43560

    desc = "; ".join(f"({_fmt(e)}, {_fmt(n)})" for e, n in pts)
    stem = (f"A four-sided parcel has corners at E,N coordinates {desc} (feet). "
            f"What is the parcel area in acres?")
    correct = f"{_fmt(acres)} ac"
    distractors = [
        f"{_fmt(area_sf / 43560 * 2)} ac",   # forgot the 1/2
        f"{_fmt(area_sf, 0)} ac",            # square feet labeled acres
        f"{_fmt(acres / 2)} ac",             # halved twice
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Shoelace: area = \u00bd|\u03a3(E\u1d62N\u1d62\u208a\u2081 \u2212 E\u1d62\u208a\u2081N\u1d62)| "
            f"= {_fmt(area_sf, 0)} ft\u00b2 = {_fmt(area_sf, 0)}/43,560 = {_fmt(acres)} acres.")
    return _mk(rng, qid, "area-coordinates", 2, stem, choices, ai, expl,
               {"corners": pts})


# ------------------------------------------------------------ horizontal curve
@register(DOMAIN, "horizontal-curve")
def gen_hcurve(rng, qid):
    D = rng.uniform(1, 8)          # degree of curve
    I = rng.uniform(12, 70)        # intersection angle, degrees
    R = 5729.58 / D
    Ir = math.radians(I)
    T = R * math.tan(Ir / 2)
    L = R * Ir
    E = R * (1 / math.cos(Ir / 2) - 1)

    ask = rng.choice(["tangent distance T", "curve length L", "external distance E"])
    vals = {"tangent distance T": T, "curve length L": L, "external distance E": E}
    val = vals[ask]
    others = [v for k, v in vals.items() if k != ask]
    stem = (f"A horizontal curve has degree of curve D = {_fmt(D)}\u00b0 and "
            f"intersection angle I = {_fmt(I)}\u00b0. What is the {ask}?")
    correct = f"{_fmt(val)} ft"
    distractors = [
        f"{_fmt(others[0])} ft",   # a different curve element
        f"{_fmt(others[1])} ft",   # the other curve element
        f"{_fmt(2 * val)} ft",     # doubled
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"R = 5729.58/D = {_fmt(R)} ft. T = R\u00b7tan(I/2) = {_fmt(T)} ft; "
            f"L = R\u00b7I(rad) = {_fmt(L)} ft; E = R(sec(I/2)\u22121) = {_fmt(E)} ft.")
    return _mk(rng, qid, "horizontal-curve", 2, stem, choices, ai, expl,
               {"D": D, "I": I, "asked": ask})


# -------------------------------------------------------------- vertical curve
@register(DOMAIN, "vertical-curve")
def gen_vcurve(rng, qid):
    g1 = rng.uniform(-4, 4)
    g2 = rng.uniform(-4, 4)
    if abs(g2 - g1) < 1.5:
        g2 = -g1 if g1 != 0 else 3.0
    L = rng.uniform(400, 900)
    pvc = rng.uniform(90, 130)
    x = rng.uniform(50, L - 50)
    A = abs(g2 - g1)
    r = (g2 - g1) / 100.0 / L
    y = pvc + (g1 / 100.0) * x + 0.5 * r * x ** 2

    stem = (f"A {_fmt(L, 0)}-ft vertical curve joins g1 = {_fmt(g1)}% to "
            f"g2 = {_fmt(g2)}%. The PVC elevation is {_fmt(pvc)} ft. What is the "
            f"elevation {_fmt(x, 0)} ft from the PVC?")
    correct = f"{_fmt(y)} ft"
    distractors = [
        f"{_fmt(pvc + (g1 / 100.0) * x)} ft",   # tangent only, no curve term
        f"{_fmt(pvc + (g2 / 100.0) * x)} ft",   # wrong grade
        f"{_fmt(y + A)} ft",
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"y = PVC + g1\u00b7x + (r/2)x\u00b2, r = A/L = {_fmt(A)}/{_fmt(L, 0)} "
            f"= {_fmt(r, 6)}/ft. y = {_fmt(pvc)} + {_fmt(g1 / 100, 5)}\u00b7{_fmt(x, 0)} "
            f"+ 0.5\u00b7{_fmt(r, 6)}\u00b7{_fmt(x, 0)}\u00b2 = {_fmt(y)} ft.")
    return _mk(rng, qid, "vertical-curve", 3, stem, choices, ai, expl,
               {"g1": g1, "g2": g2, "L": L, "pvc_elev": pvc, "x": x})


# ----------------------------------------------------------------- level notes
@register(DOMAIN, "level-notes")
def gen_levels(rng, qid):
    bm = rng.uniform(95, 110)
    bs = rng.uniform(2, 9)
    fs = rng.uniform(2, 9)
    hi = bm + bs
    tp = hi - fs

    stem = (f"Differential leveling: BM elev {_fmt(bm)} ft, backsight "
            f"{_fmt(bs)} ft, foresight {_fmt(fs)} ft on TP1. What is the "
            f"elevation of TP1?")
    correct = f"{_fmt(tp)} ft"
    distractors = [
        f"{_fmt(hi)} ft",            # HI reported as the answer
        f"{_fmt(bm + bs + fs)} ft",  # added the foresight
        f"{_fmt(bm - fs)} ft",       # skipped the HI
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"HI = {_fmt(bm)} + {_fmt(bs)} = {_fmt(hi)} ft. "
            f"TP1 = HI \u2212 FS = {_fmt(hi)} \u2212 {_fmt(fs)} = {_fmt(tp)} ft.")
    return _mk(rng, qid, "level-notes", 1, stem, choices, ai, expl,
               {"bm_elev": bm, "bs": bs, "fs": fs})


# ---------------------------------------------------------------------- stadia
@register(DOMAIN, "stadia")
def gen_stadia(rng, qid):
    s = rng.uniform(1.0, 4.0)
    alpha = rng.uniform(2, 10)
    ar = math.radians(alpha)
    D = 100 * s * math.cos(ar) ** 2
    V = 50 * s * math.sin(2 * ar)

    ask = rng.choice(["horizontal distance", "vertical component"])
    val = D if ask == "horizontal distance" else V
    stem = (f"Stadia observations: rod intercept s = {_fmt(s)} ft, vertical angle "
            f"\u03b1 = {_fmt(alpha)}\u00b0 (K = 100). What is the {ask}?")
    correct = f"{_fmt(val)} ft"
    distractors = [
        f"{_fmt(100 * s)} ft",                                    # ignored the angle
        f"{_fmt(V if ask == 'horizontal distance' else D)} ft",   # wrong component
        f"{_fmt(100 * s * math.cos(ar))} ft",                     # cos, not cos^2
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"D = K\u00b7s\u00b7cos\u00b2\u03b1 = 100\u00b7{_fmt(s)}\u00b7cos\u00b2({_fmt(alpha)}\u00b0) "
            f"= {_fmt(D)} ft. V = \u00bdK\u00b7s\u00b7sin(2\u03b1) = {_fmt(V)} ft.")
    return _mk(rng, qid, "stadia", 2, stem, choices, ai, expl,
               {"s": s, "alpha": alpha, "asked": ask})


# --------------------------------------------------------------------- volumes
@register(DOMAIN, "volumes")
def gen_volume(rng, qid):
    a1 = rng.uniform(200, 1500)
    a2 = rng.uniform(200, 1500)
    L = rng.uniform(50, 200)
    v_cy = L * (a1 + a2) / 2 / 27

    stem = (f"Two cross-sections {_fmt(L, 0)} ft apart have areas "
            f"{_fmt(a1, 0)} ft\u00b2 and {_fmt(a2, 0)} ft\u00b2. By the average "
            f"end area method, what is the volume in cubic yards?")
    correct = f"{_fmt(v_cy, 1)} CY"
    distractors = [
        f"{_fmt(L * (a1 + a2) / 2, 0)} CY",  # cubic feet labeled CY
        f"{_fmt(v_cy * 2, 1)} CY",
        f"{_fmt(L * abs(a1 - a2) / 2 / 27, 1)} CY",  # differenced areas
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"V = L(A1+A2)/2 = {_fmt(L, 0)}({_fmt(a1, 0)}+{_fmt(a2, 0)})/2 "
            f"= {_fmt(L * (a1 + a2) / 2, 0)} ft\u00b3 = /27 = {_fmt(v_cy, 1)} CY.")
    return _mk(rng, qid, "volumes", 2, stem, choices, ai, expl,
               {"A1": a1, "A2": a2, "L": L})


# ----------------------------------------------------------- error propagation
@register(DOMAIN, "error-propagation")
def gen_errprop(rng, qid):
    s1 = rng.uniform(0.01, 0.05)
    s2 = rng.uniform(0.01, 0.05)
    total = math.hypot(s1, s2)

    stem = (f"A distance is measured in two segments with standard errors "
            f"\u00b1{_fmt(s1, 4)} ft and \u00b1{_fmt(s2, 4)} ft. What is the standard "
            f"error of the total distance?")
    correct = f"\u00b1{_fmt(total, 4)} ft"
    # Distractors are separated from the answer and each other by >= 0.005,
    # so 4-decimal rounding can never collapse them (proven separation).
    distractors = [
        f"\u00b1{_fmt(s1 + s2, 4)} ft",      # linear sum (classic mistake; always larger)
        f"\u00b1{_fmt(2 * total, 4)} ft",    # doubled
        f"\u00b1{_fmt(total / 2, 4)} ft",    # halved
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"For a sum, variances add: \u03c3 = \u221a(\u03c3\u00b2\u2081 + \u03c3\u00b2\u2082) "
            f"= \u221a({_fmt(s1, 4)}\u00b2 + {_fmt(s2, 4)}\u00b2) = \u00b1{_fmt(total, 4)} ft. "
            f"Note the answer lies strictly between the largest single error "
            f"and the linear sum \u2014 a useful sanity check.")
    return _mk(rng, qid, "error-propagation", 2, stem, choices, ai, expl,
               {"sigma1": s1, "sigma2": s2})


# ----------------------------------------------------------- angular misclosure
@register(DOMAIN, "angular-misclosure")
def gen_angmis(rng, qid):
    n = rng.randint(5, 8)
    theo = (n - 2) * 180.0
    err_min = rng.uniform(0.5, 4.0) * rng.choice([1, -1])  # minutes
    obs = theo + err_min / 60.0

    stem = (f"The observed sum of interior angles of a {n}-sided closed traverse "
            f"is {_fmt(obs, 3)}\u00b0. What is the angular misclosure?")
    # format: e.g. "540° 02.3'" observed vs 540° theoretical
    correct = f"{_fmt(err_min, 1)}\u2032"
    distractors = [
        f"{_fmt(-err_min, 1)}\u2032",          # sign flipped
        f"{_fmt(err_min * 60, 0)}\u2032",      # minutes labeled as-is of seconds
        f"{_fmt(abs(err_min) / n, 2)}\u2032",  # distributed per angle
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Theoretical sum = (n\u22122)\u00b7180\u00b0 = {_fmt(theo, 0)}\u00b0. "
            f"Misclosure = observed \u2212 theoretical = {_fmt(err_min, 1)}\u2032. "
            f"(Distribute \u2212misclosure/n per angle to adjust.)")
    return _mk(rng, qid, "angular-misclosure", 1, stem, choices, ai, expl,
               {"n": n, "observed_sum": obs})
