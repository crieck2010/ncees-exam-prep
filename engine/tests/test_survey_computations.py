"""Generator correctness: every answer independently recomputed from the
question's own parameters. Catches formula bugs in the generators."""
import math
import random

import pytest

from fs_quiz import registry
from fs_quiz import engine as _engine  # noqa: F401 (registers generators)
from fs_quiz.schema import make_qid


def _gen(domain, topic, seed, i=0):
    fn = registry.get_generator(domain, topic)
    rng = random.Random(f"{fn.__name__}:{seed}:{i}")
    return fn(rng, make_qid(fn.__name__, seed, i))


def _recompute(q):
    """Independent answer string for each topic, derived only from parameters."""
    p = q.parameters
    t = q.topic
    if t == "inverse":
        dN, dE = p["N2"] - p["N1"], p["E2"] - p["E1"]
        return f"{math.degrees(math.atan2(dE, dN)) % 360:.2f}\u00b0"
    if t == "forward":
        azr = math.radians(p["az"])
        return f"{p['N1'] + p['dist'] * math.cos(azr):.2f} ft"
    if t == "traverse-misclosure":
        e = math.hypot(p["sum_lat"], p["sum_dep"])
        return f"{e:.2f} ft; 1:{p['perimeter'] / e:,.0f}"
    if t == "bowditch":
        which = "latitude" if "latitude correction" in q.stem else "departure"
        err = p["err_lat"] if which == "latitude" else p["err_dep"]
        return f"{-err * p['leg'] / p['perimeter']:.2f} ft"
    if t == "area-coordinates":
        pts = [tuple(c) for c in p["corners"]]
        s = sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1]
                for i in range(4))
        return f"{abs(s) / 2 / 43560:.2f} ac"
    if t == "horizontal-curve":
        R = 5729.58 / p["D"]
        Ir = math.radians(p["I"])
        vals = {
            "tangent distance T": R * math.tan(Ir / 2),
            "curve length L": R * Ir,
            "external distance E": R * (1 / math.cos(Ir / 2) - 1),
        }
        return f"{vals[p['asked']]:.2f} ft"
    if t == "vertical-curve":
        r = (p["g2"] - p["g1"]) / 100.0 / p["L"]
        y = p["pvc_elev"] + (p["g1"] / 100.0) * p["x"] + 0.5 * r * p["x"] ** 2
        return f"{y:.2f} ft"
    if t == "level-notes":
        return f"{p['bm_elev'] + p['bs'] - p['fs']:.2f} ft"
    if t == "stadia":
        ar = math.radians(p["alpha"])
        v = 100 * p["s"] * math.cos(ar) ** 2 if p["asked"] == "horizontal distance" \
            else 50 * p["s"] * math.sin(2 * ar)
        return f"{v:.2f} ft"
    if t == "volumes":
        return f"{p['L'] * (p['A1'] + p['A2']) / 2 / 27:.1f} CY"
    if t == "error-propagation":
        return f"\u00b1{math.hypot(p['sigma1'], p['sigma2']):.4f} ft"
    if t == "angular-misclosure":
        obs_min = (p["observed_sum"] - (p["n"] - 2) * 180.0) * 60.0
        return f"{obs_min:.1f}\u2032"
    raise AssertionError(f"no recompute for {t}")


TOPICS = registry.list_topics("survey-computations")


@pytest.mark.parametrize("topic", TOPICS)
def test_answer_matches_independent_recomputation(topic):
    for seed in (1, 7, 42):
        q = _gen("survey-computations", topic, seed)
        assert q.correct_choice == _recompute(q), (
            f"{topic} seed={seed}: {q.correct_choice!r} != {_recompute(q)!r}\n{q.stem}"
        )


@pytest.mark.parametrize("topic", TOPICS)
def test_deterministic_replay(topic):
    a = _gen("survey-computations", topic, 99)
    b = _gen("survey-computations", topic, 99)
    assert a.qid == b.qid
    assert a.to_json() == b.to_json()
    c = _gen("survey-computations", topic, 100)
    assert a.qid != c.qid


@pytest.mark.parametrize("topic", TOPICS)
def test_choices_unique_and_answer_in_range(topic):
    for seed in (3, 11):
        q = _gen("survey-computations", topic, seed)
        assert len(set(q.choices)) == 4
        assert 0 <= q.answer_index < 4
        assert q.explanation.strip()
        assert q.stem.strip()
