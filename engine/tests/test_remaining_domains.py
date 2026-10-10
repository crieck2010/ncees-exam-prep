"""v0.3.0 domains: every answer independently re-derived from parameters."""
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


def _rederive(q):
    p = q.parameters
    t = q.topic
    d = q.domain
    if d == "surveying-processes-and-methods":
        if t == "error-types":
            return p["kind"].capitalize()
        if t == "edm-ppm":
            return f"{p['D'] + p['D'] * p['ppm'] / 1e6 + p['const']:.2f} ft"
        if t == "three-wire":
            return f"{(p['upper'] + p['lower']) / 2:.2f} ft"
        if t == "curvature-refraction":
            return f"{0.574 * p['miles'] ** 2:.3f} ft"
        if t == "gnss-window":
            return f"Window {p['best']}"
        if t in ("traverse-types", "accuracy-precision"):
            return p["correct"]
    if d == "mapping-processes-and-methods":
        if t == "photo-scale":
            return f"1:{p['H_ft'] * 12.0 / p['f_in']:,.0f}"
        if t == "contour-interpolation":
            return f"{(p['target'] - p['e1']) / (p['e2'] - p['e1']) * p['L']:.2f} ft"
        if t == "utm-zone":
            return f"Zone {int((p['lon'] + 180) // 6) + 1}"
        if t in ("raster-vector", "lidar-products", "state-plane-projection"):
            return p["correct"]
    if d == "surveying-principles-geodesy":
        if t == "orthometric-height":
            return f"{p['h'] - p['N']:.2f} ft"
        if t == "combined-factor":
            return f"{p['ground'] * p['cf']:.2f} ft"
        if t in ("elevation-factor", "datums"):
            return p["correct"]
        if t == "grid-vs-ground":
            return ("The grid distance is shorter" if p["cf"] < 1
                    else "The grid distance is longer")
    if d == "business-concepts-ethics":
        return p["correct"]
    if d == "applied-math-statistics":
        if t == "law-of-sines":
            Ar, Br = math.radians(p["A"]), math.radians(p["B"])
            return f"{p['a'] * math.sin(Br) / math.sin(Ar):.2f} ft"
        if t == "law-of-cosines":
            Cr = math.radians(p["C"])
            c = math.sqrt(p["a"] ** 2 + p["b"] ** 2 - 2 * p["a"] * p["b"] * math.cos(Cr))
            return f"{c:.2f} ft"
        if t == "std-error-mean":
            return f"{p['s'] / math.sqrt(p['n']):.4f} ft"
        if t == "confidence-intervals":
            return {1: "68%", 2: "95%", 3: "99.7%"}[p["k"]]
        if t == "significant-figures":
            return str(p["count"])
        if t == "unit-conversions":
            if p["kind"] == "sqft-to-acres":
                return f"{p['sqft'] / 43560:.2f} acres"
            return f"{p['ft'] * 0.3048:.2f} m"
    raise AssertionError(f"no rederive for {d}/{t}")


DOMAINS = [
    "surveying-processes-and-methods",
    "mapping-processes-and-methods",
    "surveying-principles-geodesy",
    "business-concepts-ethics",
    "applied-math-statistics",
]

CASES = [(d, t) for d in DOMAINS for t in registry.list_topics(d)]


@pytest.mark.parametrize("domain,topic", CASES)
def test_answer_matches_independent_rederivation(domain, topic):
    for seed in (1, 7, 42):
        q = _gen(domain, topic, seed)
        assert q.correct_choice == _rederive(q), (
            f"{domain}/{topic} seed={seed}:\n  got  {q.correct_choice!r}\n"
            f"  want {_rederive(q)!r}\n{q.stem}"
        )


@pytest.mark.parametrize("domain,topic", CASES)
def test_deterministic_replay(domain, topic):
    a = _gen(domain, topic, 99)
    b = _gen(domain, topic, 99)
    assert a.to_json() == b.to_json()
    assert _gen(domain, topic, 100).qid != a.qid


@pytest.mark.parametrize("domain,topic", CASES)
def test_choices_unique_and_answer_in_range(domain, topic):
    for seed in (3, 11):
        q = _gen(domain, topic, seed)
        assert len(set(q.choices)) == 4
        assert 0 <= q.answer_index < 4
        assert q.explanation.strip()


def test_expected_topic_lists():
    assert registry.list_topics("surveying-processes-and-methods") == [
        "accuracy-precision", "curvature-refraction", "edm-ppm", "error-types",
        "gnss-window", "three-wire", "traverse-types",
    ]
    assert registry.list_topics("mapping-processes-and-methods") == [
        "contour-interpolation", "lidar-products", "photo-scale",
        "raster-vector", "state-plane-projection", "utm-zone",
    ]
    assert registry.list_topics("surveying-principles-geodesy") == [
        "combined-factor", "datums", "elevation-factor", "grid-vs-ground",
        "orthometric-height",
    ]
    assert registry.list_topics("business-concepts-ethics") == [
        "conflict-of-interest", "contract-elements", "duty-hierarchy",
        "fee-structures", "sealing",
    ]
    assert registry.list_topics("applied-math-statistics") == [
        "confidence-intervals", "law-of-cosines", "law-of-sines",
        "significant-figures", "std-error-mean", "unit-conversions",
    ]


def test_all_seven_domains_total_48_topics():
    total = sum(len(registry.list_topics(d)) for d in registry.list_domains())
    assert total == 48
    assert len(registry.list_domains()) == 7
