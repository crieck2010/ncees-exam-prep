"""Phase 2 domain: boundary-law-and-real-property (19-29 FS questions, the
heaviest area).

7 scenario generators. Each takes ``(rng, qid)`` and returns a Question.
Scenarios are synthesized from fact-pattern templates with randomized names,
dates, and measurements — original content, never NCEES or publisher items.

Answer derivation lives in ``parameters`` so tests can independently
re-derive every correct choice (see tests/test_boundary_law.py).
"""
from __future__ import annotations

from fs_quiz.generators.survey_computations import _fmt, _mcq
from fs_quiz.registry import register
from fs_quiz.schema import SCHEMA_VERSION, Question

DOMAIN = "boundary-law-and-real-property"


def _mk(rng, qid, topic, difficulty, stem, choices, answer_index,
        explanation, parameters):
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
        seed=hash(qid) % (2 ** 31),
    )


_NAMES = ["Alvarez", "Becker", "Chen", "Diaz", "Ellis", "Foster", "Garcia",
          "Hughes", "Ivers", "Jensen", "Kowalski", "Larsen"]


# ------------------------------------------------------- hierarchy of calls
# rank: lower number = higher legal dignity
_CALLS = [
    (0, "a natural monument", "the thread of {creek} (called as the boundary)"),
    (1, "an artificial monument", "an original {pin} set in {year}"),
    (2, "an adjoiner", "the adjoining {name} parcel line"),
    (3, "a distance", "a deed call of {dist} feet"),
    (4, "a direction", "a deed bearing of {brg}"),
    (5, "an area", "a stated area of {area} acres"),
    (6, "coordinates", "a listed coordinate pair N {n}, E {e}"),
]

_HIERARCHY_LINE = ("natural monuments > artificial monuments > adjoiners > "
                   "distance > direction > area > coordinates")


@register(DOMAIN, "hierarchy-of-calls")
def gen_hierarchy(rng, qid):
    a, b = rng.sample(_CALLS, 2)
    high, low = (a, b) if a[0] < b[0] else (b, a)
    creek = rng.choice(["Miller Creek", "Deer Run", "the north fork of Baker River"])
    pin = rng.choice(["1-inch iron pin", "stone monument", "brass disk"])
    year = rng.randint(1948, 1998)
    name = rng.choice(_NAMES)
    fmt_kw = {"creek": creek, "pin": pin, "year": year, "name": name,
              "dist": _fmt(rng.uniform(80, 400)), "brg": f"N {_fmt(rng.uniform(10, 80))} E",
              "area": _fmt(rng.uniform(1, 10)), "n": _fmt(rng.uniform(1000, 9000)),
              "e": _fmt(rng.uniform(1000, 9000))}
    high_desc = f"{high[1].capitalize()}: {high[2].format(**fmt_kw)}"
    low_desc = f"{low[1].capitalize()}: {low[2].format(**fmt_kw)}"
    first, second = (high_desc, low_desc) if rng.random() < 0.5 else (low_desc, high_desc)

    stem = (f"A deed and the ground disagree. The two conflicting pieces of "
            f"evidence are (A) {first} and (B) {second}. Under the hierarchy "
            f"of calls, which controls the boundary location?")
    correct = f"The boundary follows {high_desc[0].lower() + high_desc[1:]}"
    distractors = [
        f"The boundary follows {low_desc[0].lower() + low_desc[1:]}",
        "The most recently created evidence controls",
        "The two are averaged and the boundary is set midway",
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Hierarchy of calls: {_HIERARCHY_LINE}. {high[1].capitalize()} "
            f"outranks {low[1]} — monuments beat measurements because they "
            f"best reflect the original parties' intent.")
    return _mk(rng, qid, "hierarchy-of-calls", 1, stem, choices, ai, expl,
               {"high_rank": high[0], "high_kind": high[1],
                "high_desc": correct,
                "low_rank": low[0], "low_kind": low[1]})


# ------------------------------------------------------- senior/junior rights
_SENIOR = "A owns the disputed strip \u2014 senior rights prevail"
_JUNIOR = "B owns the disputed strip \u2014 the later deed controls"
_APPORTION = ("The overlap/gap is apportioned equally \u2014 simultaneous "
              "conveyances, no seniority")
_GRANTOR = ("The common grantor retains it \u2014 the strip was never conveyed")


@register(DOMAIN, "senior-junior-rights")
def gen_senior(rng, qid):
    a, b, o = rng.sample(_NAMES, 3)
    y1 = rng.randint(1960, 1990)
    width = rng.randint(2, 12)
    order = rng.choice(["sequential", "simultaneous"])
    issue = rng.choice(["overlap", "gap"])
    if order == "sequential":
        y2 = y1 + rng.randint(2, 15)
        order_txt = f"in {y1} {o} conveyed the west parcel to {a}; in {y2} {o} conveyed the east parcel to {b}"
        correct = _SENIOR if issue == "overlap" else _GRANTOR
        rule = (f"Sequential conveyances create senior (first) and junior (second) "
                f"rights. In an overlap the senior grantee, {a}, prevails."
                if issue == "overlap" else
                f"The gap was described by neither deed, so it was never "
                f"conveyed \u2014 it remains with the common grantor, {o}.")
    else:
        order_txt = f"{o} conveyed the west parcel to {a} and the east parcel to {b} in the same instrument"
        correct = _APPORTION
        rule = ("Simultaneous conveyances have no seniority \u2014 the "
                "overlap/gap is apportioned equally between the grantees.")

    stem = (f"{order_txt}. The two descriptions {issue} by {width} feet. "
            f"Who owns the {issue} strip?")
    distractors = [c for c in (_SENIOR, _JUNIOR, _APPORTION, _GRANTOR) if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = rule + f" ({a} = first/senior grantee, {b} = second/junior grantee.)"
    return _mk(rng, qid, "senior-junior-rights", 2, stem, choices, ai, expl,
               {"order": order, "issue": issue,
                "senior": a, "junior": b, "grantor": o})


# --------------------------------------------------------------------- PLSS
def _plss_col_from_west(s: int) -> int:
    r, k = (s - 1) // 6, (s - 1) % 6
    return (5 - k) if r % 2 == 0 else k


def _plss_section(row: int, col_w: int) -> int:
    k = (5 - col_w) if row % 2 == 0 else col_w
    return 6 * row + 1 + k


def _south_of(s: int):
    r = (s - 1) // 6
    if r == 5:
        return None
    return _plss_section(r + 1, _plss_col_from_west(s))


@register(DOMAIN, "plss")
def gen_plss(rng, qid):
    if rng.random() < 0.6:
        # aliquot acres
        parts, divisor = [], 1
        for _ in range(rng.randint(1, 3)):
            half = rng.random() < 0.5
            if half:
                parts.append(rng.choice(["N1/2", "S1/2", "E1/2", "W1/2"]))
                divisor *= 2
            else:
                parts.append(rng.choice(["NE1/4", "NW1/4", "SE1/4", "SW1/4"]))
                divisor *= 4
        desc = " of ".join(parts)
        acres = 640 / divisor
        sec = rng.randint(1, 36)
        stem = (f"How many acres are in the {desc} of Section {sec}?")
        correct = f"{_fmt(acres)} acres"
        distractors = [f"{_fmt(acres * 2)} acres", f"{_fmt(acres / 2)} acres",
                       f"{_fmt(acres * 4)} acres"]
        choices, ai = _mcq(rng, correct, distractors)
        expl = (f"A section is 640 acres. {' Halves divide by 2; quarters divide by 4.'.strip()} "
                f"640 / {divisor} = {_fmt(acres)} acres.")
        params = {"subtype": "acres", "divisor": divisor}
    else:
        # section position
        s = rng.randint(1, 30)
        target = _south_of(s)
        stem = (f"In a standard PLSS township, which section lies directly "
                f"south of Section {s}?")
        correct = f"Section {target}"
        distractors = [f"Section {s + 6}", f"Section {s - 6}", f"Section {s + 1}"]
        # dedupe in case the naive distractors collide with the answer
        distractors = [d for d in distractors if d != correct][:3]
        while len(distractors) < 3:
            cand = f"Section {rng.randint(1, 36)}"
            if cand != correct and cand not in distractors:
                distractors.append(cand)
        choices, ai = _mcq(rng, correct, distractors)
        expl = (f"Sections are numbered boustrophedon (1\u20136 east-to-west across "
                f"the north tier, then snaking). Directly south of Section {s} "
                f"is Section {target} \u2014 not simply {s}\u00b16, because alternate "
                f"tiers run opposite directions.")
        params = {"subtype": "south", "section": s}
    return _mk(rng, qid, "plss", 2, stem, choices, ai, expl, params)


# ------------------------------------------------------------ water boundaries
_WATER = {
    "accretion": ("Over about 30 years the river's east bank has gradually and "
                  "imperceptibly built outward by roughly {w} feet of new dry land.",
                  True),
    "avulsion": ("During a single flood event last spring the river cut a new "
                 "channel about {w} feet east of its former course.",
                 False),
    "reliction": ("Over several decades the lake level has gradually receded, "
                  "exposing about {w} feet of new shoreline.",
                  True),
    "erosion": ("Over about 20 years the river has slowly eaten away roughly "
                "{w} feet of the west bank.",
                  True),
}
_MOVES = "The boundary moves with the water \u2014 gradual, imperceptible change"
_STAYS = "The boundary stays at the former location \u2014 sudden change (avulsion)"


@register(DOMAIN, "water-boundaries")
def gen_water(rng, qid):
    name = rng.choice(_NAMES)
    process, (tmpl, moves) = rng.choice(list(_WATER.items()))
    w = rng.randint(10, 200)
    stem = (tmpl.format(w=w) + f" {name} owns the riparian parcel. "
            f"Where is the water boundary now?")
    correct = _MOVES if moves else _STAYS
    distractors = [
        _STAYS if moves else _MOVES,
        "The riparian owner loses all rights to the affected land",
        "The boundary is fixed at the original government meander line",
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"This is {process}: "
            f"{'gradual and imperceptible, so the boundary moves with the water.' if moves else 'a sudden avulsive change, so the boundary remains where the watercourse was.'}")
    return _mk(rng, qid, "water-boundaries", 2, stem, choices, ai, expl,
               {"process": process, "moves": moves})


# ------------------------------------------------------------------ easements
_EASE_TYPES = [
    "Express grant \u2014 created by the deed itself",
    "Easement by necessity \u2014 landlocked parcel, no other access",
    "Prescriptive easement \u2014 long, open, hostile use ripened into a right",
    "Easement in gross \u2014 benefits a person/company, not a parcel",
    "Terminated by merger \u2014 dominant and servient estates united",
]
_EASE_FACTS = [
    ("The deed conveying Lot 4 expressly reserves a 20-foot access easement "
     "across Lot 5 for the benefit of Lot 4.", 0),
    ("Parcel B is completely landlocked; the only practical access is across "
     "Parcel A, from which B was severed. No easement was ever written.", 1),
    ("For 26 years (statutory period 20) neighbors have openly driven across "
     "the corner of a vacant lot, without permission, to reach the lake.", 2),
    ("The power company holds a 30-foot corridor easement for its transmission "
     "line; it owns no adjoining land.", 3),
    ("Elena owned both the dominant and servient parcels and then sold the "
     "servient parcel without reserving the driveway easement.", 4),
]


@register(DOMAIN, "easements")
def gen_easement(rng, qid):
    facts, correct_idx = rng.choice(_EASE_FACTS)
    correct = _EASE_TYPES[correct_idx]
    distractors = [t for i, t in enumerate(_EASE_TYPES) if i != correct_idx]
    rng.shuffle(distractors)
    stem = facts + " What best describes this easement situation?"
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = f"The facts match: {correct}."
    return _mk(rng, qid, "easements", 2, stem, choices, ai, expl,
               {"correct_type": correct})


# ----------------------------------------------------------- adverse possession
_AP_ELEMENTS = ["actual possession", "open and notorious use",
                "exclusive possession", "hostile claim (without permission)",
                "continuous possession for the statutory period"]

_AP_FACTS = {
    None: ("For 23 years (statutory period 20) Ruth has fenced, gardened, and "
           "paid taxes on the disputed strip \u2014 openly, without anyone's "
           "permission, excluding all others, without interruption."),
    "actual possession": ("Ruth has never set foot on the strip; she merely "
                          "asserts ownership on paper. She has been open about "
                          "the claim for 23 years, excluded others, acted "
                          "without permission, and never interrupted it."),
    "open and notorious use": ("Ruth has used the strip only at night and "
                                "actively concealed the use from the owner for "
                                "23 years, though her possession was actual, "
                                "exclusive, hostile, and continuous."),
    "exclusive possession": ("Ruth has shared the strip with the record owner "
                             "and several neighbors throughout the 23 years, "
                             "though her use was actual, open, hostile, and "
                             "continuous."),
    "hostile claim (without permission)": ("Ruth has occupied the strip for 23 "
                                           "years under the record owner's "
                                           "written permission, though her "
                                           "possession was actual, open, "
                                           "exclusive, and continuous."),
    "continuous possession for the statutory period": ("Ruth occupied the strip "
                                                      "openly and exclusively "
                                                      "without permission, but "
                                                      "abandoned it entirely "
                                                      "for 4 of the last 23 "
                                                      "years."),
}


@register(DOMAIN, "adverse-possession")
def gen_adverse(rng, qid):
    missing = rng.choice([None] + _AP_ELEMENTS)
    facts = _AP_FACTS[missing]
    stem = (facts + " The statutory period is 20 years. "
            "Does Ruth's adverse possession claim succeed?")
    yes = "Yes \u2014 all five elements are satisfied"
    if missing is None:
        correct = yes
        others = [f"No \u2014 fails the {e} element"
                  for e in rng.sample(_AP_ELEMENTS, 3)]
    else:
        correct = f"No \u2014 fails the {missing} element"
        others = [yes] + [f"No \u2014 fails the {e} element"
                          for e in rng.sample([e for e in _AP_ELEMENTS
                                               if e != missing], 2)]
    choices, ai = _mcq(rng, correct, others)
    expl = ("All five elements \u2014 actual, open/notorious, exclusive, hostile, "
            "continuous \u2014 must be met." +
            (" They are." if missing is None else
             f" The claim fails on: {missing}."))
    return _mk(rng, qid, "adverse-possession", 3, stem, choices, ai, expl,
               {"missing_element": missing})


# ------------------------------------------------------------- deeds/recording
_DEED_ANSWERS = {
    "strongest": "General warranty deed",
    "grantor-only": "Special warranty deed",
    "no-warranty": "Quitclaim deed",
}
_DEED_ASKS = {
    "strongest": ("A buyer wants the strongest possible guarantee of title "
                  "against defects arising at any time in the chain of title. "
                  "Which deed should the buyer insist on?"),
    "grantor-only": ("A seller will warrant the title only against defects "
                     "that arose during the seller's own period of ownership. "
                     "Which deed fits?"),
    "no-warranty": ("A grantor wants to convey whatever interest they may have, "
                    "with no warranties of title at all. Which deed fits?"),
}
_DEED_CHOICES = ["General warranty deed", "Special warranty deed",
                 "Quitclaim deed", "Sheriff's deed"]

_RACE = "race statute \u2014 the first to record wins"
_NOTICE = "notice statute \u2014 a bona fide purchaser without notice wins"
_RACENOTICE = ("race-notice statute \u2014 a bona fide purchaser who records "
              "first wins")


@register(DOMAIN, "deeds-recording")
def gen_deeds(rng, qid):
    if rng.random() < 0.5:
        ask = rng.choice(list(_DEED_ASKS))
        stem = _DEED_ASKS[ask]
        correct = _DEED_ANSWERS[ask]
        distractors = [d for d in _DEED_CHOICES if d != correct]
        choices, ai = _mcq(rng, correct, distractors[:3])
        expl = (f"{correct}: "
                + {"strongest": "warrants against all defects in the chain of title.",
                   "grantor-only": "warrants only against the grantor's own acts.",
                   "no-warranty": "conveys whatever interest exists, warranting nothing."}[ask])
        params = {"subtype": "deed-type", "ask": ask}
    else:
        act = rng.choice(["race", "notice", "race-notice"])
        notice = rng.random() < 0.5
        act_txt = {"race": _RACE, "notice": _NOTICE,
                   "race-notice": _RACENOTICE}[act]
        a, b = rng.sample(_NAMES, 2)
        stem = (f"O conveys Blackacre to {a}, who does not record. O then conveys "
                f"Blackacre to {b}, who {'knew about the first conveyance' if notice else 'had no notice of it'} "
                f"and records first. This state follows a {act_txt}. Who prevails?")
        b_wins = (act == "race") or (not notice)  # race: record-first wins; else BFP rule
        correct = (f"{b} prevails \u2014 first to record" if b_wins and act != "notice"
                   else f"{b} prevails \u2014 bona fide purchaser without notice" if b_wins
                   else f"{a} prevails \u2014 {b} had notice and is not a bona fide purchaser")
        distractors = [
            f"{a} prevails \u2014 first in time, first in right",
            f"{b} prevails \u2014 possession is nine-tenths of the law",
            f"They take as tenants in common, splitting Blackacre equally",
        ]
        choices, ai = _mcq(rng, correct, distractors)
        expl = (f"Under a {act_txt}: "
                + (f"{b} recorded first, so {b} wins." if act == "race" else
                   f"{b} is a bona fide purchaser without notice, so {b} wins." if not notice else
                   f"{b} had notice and is not a bona fide purchaser, so {a} wins."))
        params = {"subtype": "recording-act", "act": act, "b_had_notice": notice,
                  "b_wins": b_wins}
    return _mk(rng, qid, "deeds-recording", 2, stem, choices, ai, expl, params)
