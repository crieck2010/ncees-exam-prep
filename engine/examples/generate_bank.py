"""Generate a full survey-computations bank and print a sample question.

Usage: python3 examples/generate_bank.py [--n 10] [--seed 42] [--out bank.json]
"""
import argparse
import json
import sys

from fs_quiz.engine import QuizEngine


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="bank.json")
    args = p.parse_args()

    eng = QuizEngine()
    bank = eng.generate_bank(n_per_topic=args.n, seed=args.seed)
    bank = [q for q in bank if q.domain == "survey-computations"]
    eng.export_bank(bank, args.out)

    sample = bank[0]
    print(f"wrote {len(bank)} questions -> {args.out}\n")
    print(f"[{sample.domain} / {sample.topic} / difficulty {sample.difficulty}]")
    print(sample.stem)
    for i, c in enumerate(sample.choices):
        print(f"  {'ABCD'[i]}. {c}")
    print(f"\nAnswer: {'ABCD'[sample.answer_index]}")
    print(f"Why: {sample.explanation}")


if __name__ == "__main__":
    sys.exit(main())
