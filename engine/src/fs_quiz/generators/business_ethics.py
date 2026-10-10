"""Domain: business-concepts-ethics (11-17 FS questions).

5 scenario generators: duty hierarchy, sealing rules, contract elements,
fee structures, conflicts of interest. Original scenarios throughout.
"""
from __future__ import annotations

from fs_quiz.generators.survey_computations import _fmt, _mcq
from fs_quiz.registry import register
from fs_quiz.schema import SCHEMA_VERSION, Question

DOMAIN = "business-concepts-ethics"


def _mk(rng, qid, topic, difficulty, stem, choices, answer_index,
        explanation, parameters):
    return Question(
        qid=qid, schema_version=SCHEMA_VERSION, domain=DOMAIN, topic=topic,
        difficulty=difficulty, stem=stem, choices=choices,
        answer_index=answer_index, explanation=explanation,
        parameters=parameters, seed=hash(qid) % (2 ** 31),
    )


# ------------------------------------------------------------- duty hierarchy
_DUTY_FACTS = [
    ("A client pressures the surveyor to skip safety checks to meet a deadline, "
     "endangering the crew and the public.",
     "Protect public health, safety, and welfare first \u2014 decline the shortcut",
     "The surveyor's first duty is to the public; no client instruction overrides it."),
    ("An employer asks the surveyor to certify a boundary they never field-checked.",
     "Refuse to certify \u2014 only seal work prepared under your responsible charge",
     "Certifying unchecked work endangers the public and violates the duty of competence and honesty."),
    ("A developer offers a bonus for moving a boundary line to gain buildable area.",
     "Decline \u2014 the surveyor locates existing boundaries; they do not create favorable ones",
     "Loyalty to a client never justifies misrepresenting a boundary to the public and adjoining owners."),
]
_DUTY_WRONG = ["Obey the client \u2014 the client pays the bills",
               "Obey the employer \u2014 follow orders quietly",
               "Do it but document nothing, to limit liability"]


@register(DOMAIN, "duty-hierarchy")
def gen_duty(rng, qid):
    facts, correct, why = rng.choice(_DUTY_FACTS)
    stem = facts + " What is the surveyor's proper course of action?"
    distractors = rng.sample(_DUTY_WRONG, 3)
    choices, ai = _mcq(rng, correct, distractors)
    return _mk(rng, qid, "duty-hierarchy", 2, stem, choices, ai, why,
               {"correct": correct})


# ------------------------------------------------------------- sealing
_SEAL_FACTS = [
    ("A licensed surveyor is asked to seal a plat prepared entirely by another "
     "firm, which they only glanced at.",
     "No \u2014 a seal certifies work prepared under the sealer's responsible charge",
     "Sealing unchecked work misrepresents responsibility and is a classic violation."),
    ("A licensed surveyor seals a boundary survey their own crew performed "
     "under their direct supervision.",
     "Yes \u2014 the work was prepared under their responsible charge",
     "Responsible charge (direct supervision and control) is the standard."),
    ("A surveyor is asked to seal a document for use in a state where they "
     "hold no license.",
     "No \u2014 sealing is only valid where the surveyor is licensed",
     "A seal carries jurisdictional authority; using it elsewhere is unauthorized practice."),
]
_SEAL_WRONG = ["Yes \u2014 a quick review is enough",
               "Yes \u2014 any licensed surveyor may seal any survey document",
               "No \u2014 surveyors may never seal plats"]


@register(DOMAIN, "sealing")
def gen_sealing(rng, qid):
    facts, correct, why = rng.choice(_SEAL_FACTS)
    stem = facts + " May the surveyor properly seal it?"
    distractors = [w for w in _SEAL_WRONG if w != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    return _mk(rng, qid, "sealing", 2, stem, choices, ai, why,
               {"correct": correct})


# ------------------------------------------------------------- contract elements
_CONTRACT_FACTS = [
    ("The parties agree the surveyor will falsify a boundary location for a fee.",
     "Legal purpose",
     "A contract with an unlawful purpose is void \u2014 no enforceable agreement exists."),
    ("A 16-year-old, unemancipated minor signs a surveying services agreement alone.",
     "Competent parties",
     "Minors generally lack capacity to contract; the agreement is voidable."),
    ("The client promises future referrals instead of any payment for the work.",
     "Consideration",
     "Without consideration (value exchanged), there is no binding contract."),
]
_CONTRACT_CHOICES = ["Offer and acceptance", "Consideration", "Legal purpose",
                     "Competent parties"]


@register(DOMAIN, "contract-elements")
def gen_contract(rng, qid):
    facts, correct, why = rng.choice(_CONTRACT_FACTS)
    stem = facts + " Which required element of a valid contract is missing?"
    distractors = [c for c in _CONTRACT_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    return _mk(rng, qid, "contract-elements", 2, stem, choices, ai, why,
               {"correct": correct})


# ------------------------------------------------------------- fee structures
_FEE_FACTS = [
    ("A 0.5-acre residential lot survey with a clearly defined scope and "
     "no unusual complications.",
     "Lump sum",
     "Well-defined scope and predictable effort \u2014 the client gets price certainty."),
    ("A multi-phase ALTA survey where the title commitment keeps changing and "
     "the effort is genuinely unpredictable.",
     "Time and materials (hourly), ideally with a not-to-exceed cap",
     "Uncertain scope makes fixed pricing a gamble for one side; hourly with a cap shares the risk fairly."),
    ("Construction layout billed per stake set over a six-month project.",
     "Unit price",
     "Repetitive, countable work units \u2014 pay per unit placed."),
]
_FEE_CHOICES = ["Lump sum", "Time and materials (hourly), ideally with a not-to-exceed cap",
                "Unit price", "Contingency fee (percentage of project value)"]


@register(DOMAIN, "fee-structures")
def gen_fee(rng, qid):
    facts, correct, why = rng.choice(_FEE_FACTS)
    stem = facts + " Which fee structure is most appropriate?"
    distractors = [c for c in _FEE_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    return _mk(rng, qid, "fee-structures", 1, stem, choices, ai, why,
               {"correct": correct})


# ------------------------------------------------------------- conflict of interest
_CONFLICT_FACTS = [
    ("The surveyor personally owns the parcel adjoining the client's project, "
     "and the boundary location affects both values.",
     "Disclose the interest in writing and withdraw if impartiality cannot be maintained",
     "A personal stake in the outcome is a textbook conflict \u2014 disclosure is mandatory, withdrawal follows if judgment could be biased."),
    ("The surveyor's firm is asked to survey a boundary dispute between two "
     "of its own current clients.",
     "Disclose to both clients and proceed only with informed written consent, or decline",
     "Dual representation requires informed consent from everyone affected \u2014 otherwise decline the work."),
]
_CONFLICT_WRONG = ["Say nothing \u2014 professionalism means handling it quietly",
                   "Proceed normally; personal interests do not matter",
                   "Resolve it by favoring the higher-paying client"]


@register(DOMAIN, "conflict-of-interest")
def gen_conflict(rng, qid):
    facts, correct, why = rng.choice(_CONFLICT_FACTS)
    stem = facts + " What should the surveyor do?"
    distractors = rng.sample(_CONFLICT_WRONG, 3)
    choices, ai = _mcq(rng, correct, distractors)
    return _mk(rng, qid, "conflict-of-interest", 2, stem, choices, ai, why,
               {"correct": correct})
