"""Boundary-law correctness: every answer independently re-derived from the
question's parameters (or parsed from its stem) — never parroted."""
import random
import re

import pytest

from fs_quiz import registry
from fs_quiz import engine as _engine  # noqa: F401 (registers generators)
from fs_quiz.schema import make_qid
from fs_quiz.generators import boundary_law as bl

DOMAIN = "boundary-law-and-real-property"


def _gen(topic, seed, i=0):
    fn = registry.get_generator(DOMAIN, topic)
    rng = random.Random(f"{fn.__name__}:{seed}:{i}")
    return fn(rng, make_qid(fn.__name__, seed, i))


def _plss_south_of(s):
    """Independent reimplementation of the boustrophedon south-neighbor rule."""
    r, k = (s - 1) // 6, (s - 1) % 6
    col_w = (5 - k) if r % 2 == 0 else k
    r2 = r + 1
    k2 = (5 - col_w) if r2 % 2 == 0 else col_w
    return 6 * r2 + 1 + k2


def _rederive(q):
    p = q.parameters
    t = q.topic
    if t == "hierarchy-of-calls":
        assert p["high_rank"] < p["low_rank"], "high must outrank low"
        return p["high_desc"]
    if t == "senior-junior-rights":
        return {
            ("sequential", "overlap"): bl._SENIOR,
            ("sequential", "gap"): bl._GRANTOR,
            ("simultaneous", "overlap"): bl._APPORTION,
            ("simultaneous", "gap"): bl._APPORTION,
        }[(p["order"], p["issue"])]
    if t == "plss":
        if p["subtype"] == "acres":
            return f"{640 / p['divisor']:.2f} acres"
        return f"Section {_plss_south_of(p['section'])}"
    if t == "water-boundaries":
        return bl._MOVES if p["moves"] else bl._STAYS
    if t == "easements":
        return p["correct_type"]
    if t == "adverse-possession":
        m = p["missing_element"]
        if m is None:
            return "Yes \u2014 all five elements are satisfied"
        return f"No \u2014 fails the {m} element"
    if t == "deeds-recording":
        if p["subtype"] == "deed-type":
            return bl._DEED_ANSWERS[p["ask"]]
        a = re.search(r"O conveys Blackacre to (\w+), who does not record", q.stem).group(1)
        b = re.search(r"O then conveys Blackacre to (\w+), who", q.stem).group(1)
        b_wins = (p["act"] == "race") or (not p["b_had_notice"])
        if b_wins and p["act"] != "notice":
            return f"{b} prevails \u2014 first to record"
        if b_wins:
            return f"{b} prevails \u2014 bona fide purchaser without notice"
        return f"{a} prevails \u2014 {b} had notice and is not a bona fide purchaser"
    raise AssertionError(f"no rederive for {t}")


TOPICS = registry.list_topics(DOMAIN)


@pytest.mark.parametrize("topic", TOPICS)
def test_answer_matches_independent_rederivation(topic):
    for seed in (1, 7, 42):
        q = _gen(topic, seed)
        assert q.correct_choice == _rederive(q), (
            f"{topic} seed={seed}:\n  got  {q.correct_choice!r}\n  want {_rederive(q)!r}\n{q.stem}"
        )


@pytest.mark.parametrize("topic", TOPICS)
def test_deterministic_replay(topic):
    a = _gen(topic, 99)
    b = _gen(topic, 99)
    assert a.to_json() == b.to_json()
    assert _gen(topic, 100).qid != a.qid


@pytest.mark.parametrize("topic", TOPICS)
def test_choices_unique_and_answer_in_range(topic):
    for seed in (3, 11):
        q = _gen(topic, seed)
        assert len(set(q.choices)) == 4
        assert 0 <= q.answer_index < 4
        assert q.explanation.strip()


def test_domain_has_seven_topics():
    assert TOPICS == [
        "adverse-possession",
        "deeds-recording",
        "easements",
        "hierarchy-of-calls",
        "plss",
        "senior-junior-rights",
        "water-boundaries",
    ]
