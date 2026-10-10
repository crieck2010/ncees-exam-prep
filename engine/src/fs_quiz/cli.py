"""Thin CLI over the engine. All math lives in the generators; this only
parses args, prints, and reads stdin.
"""
from __future__ import annotations

import argparse
import sys

from fs_quiz import registry
from fs_quiz.engine import QuizEngine


def cmd_list_domains(args):
    for d in registry.list_domains():
        topics = registry.list_topics(d)
        print(f"{d} ({len(topics)} topics)")
        for t in topics:
            print(f"    {t}")


def cmd_generate(args):
    eng = QuizEngine()
    if args.all:
        bank = eng.generate_bank(n_per_topic=args.n, seed=args.seed)
    else:
        bank = eng.generate(args.domain, args.topic, n=args.n, seed=args.seed)
    eng.export_bank(bank, args.out)
    print(f"wrote {len(bank)} questions -> {args.out}")


def cmd_quiz(args):
    eng = QuizEngine()
    bank = eng.import_bank(args.bank)
    answers = {}
    letters = "ABCD"
    for i, q in enumerate(bank, 1):
        print(f"\n[{i}/{len(bank)}] ({q.domain} / {q.topic} / difficulty {q.difficulty})")
        print(q.stem)
        for j, c in enumerate(q.choices):
            print(f"  {letters[j]}. {c}")
        while True:
            sel = input("Your answer (A-D, or Q to quit): ").strip().upper()
            if sel == "Q":
                return _report(eng, bank, answers)
            if sel in letters:
                answers[q.qid] = letters.index(sel)
                break
    return _report(eng, bank, answers)


def _report(eng, bank, answers):
    summary = eng.grade(bank, answers)
    print(f"\nScore: {summary['correct']}/{summary['total']} ({summary['score_pct']}%)")
    for r in summary["results"]:
        if not r["is_correct"]:
            q = next(q for q in bank if q.qid == r["qid"])
            print(f"\nMISSED [{q.topic}]: {q.stem}")
            print(f"  Correct: {q.correct_choice}")
            print(f"  Why: {q.explanation}")
    return 0 if summary["score_pct"] >= 70 else 1


def cmd_validate(args):
    import json
    from fs_quiz.contract import validate_bank_dict
    with open(args.bank) as f:
        payload = json.load(f)
    errors = validate_bank_dict(payload)
    if errors:
        print(f"INVALID: {len(errors)} contract violation(s) in {args.bank}")
        for e in errors[:10]:
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
        return 1
    n = payload["question_count"]
    print(f"VALID: {args.bank} — schema v1, {n} questions, "
          f"{len({q['domain'] for q in payload['questions']})} domains")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="fs-quiz", description="FS exam question-bank CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-domains", help="list domains and topics").set_defaults(
        func=cmd_list_domains)

    g = sub.add_parser("generate", help="generate a question bank JSON file")
    g.add_argument("--domain", default="survey-computations")
    g.add_argument("--topic", default=None)
    g.add_argument("--all", action="store_true", help="all domains/topics")
    g.add_argument("--n", type=int, default=10)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--out", default="bank.json")
    g.set_defaults(func=cmd_generate)

    q = sub.add_parser("quiz", help="take an interactive quiz from a bank file")
    q.add_argument("--bank", required=True)
    q.set_defaults(func=cmd_quiz)

    v = sub.add_parser("validate", help="validate a bank file against the v1 contract")
    v.add_argument("--bank", required=True)
    v.set_defaults(func=cmd_validate)

    args = p.parse_args(argv)
    if args.cmd == "generate" and not args.all and not args.topic:
        p.error("--topic is required unless --all is given")
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
