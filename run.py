#!/usr/bin/env python3
"""Root task runner and developer CLI for the exam-prep monorepo."""

import argparse
import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(ROOT_DIR, "engine")
MOBILE_DIR = os.path.join(ROOT_DIR, "mobile")


def run_cmd(cmd, cwd=ROOT_DIR):
    print(f"==> [{cwd}] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def test_engine():
    """Run pytest on the Python question generator engine."""
    print("Running engine tests...")
    env = os.environ.copy()
    src_dir = os.path.join(ENGINE_DIR, "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else src_dir
    cmd = [sys.executable, "-m", "pytest", os.path.join(ENGINE_DIR, "tests"), "-v"]
    print(f"==> [{ENGINE_DIR}] {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=ENGINE_DIR, env=env)
    if res.returncode != 0:
        sys.exit(res.returncode)


def generate_banks(seeds, n):
    """Generate fresh question banks using the engine into mobile assets."""
    print(f"Generating banks with seeds {seeds} (n={n} per topic)...")
    cmd = [
        sys.executable,
        os.path.join(MOBILE_DIR, "tools", "generate_banks.py"),
        "--n", str(n),
        "--seeds"
    ] + [str(s) for s in seeds]
    run_cmd(cmd, cwd=ROOT_DIR)


def test_mobile():
    """Run Flutter tests in mobile/."""
    print("Running mobile Flutter tests...")
    run_cmd(["flutter", "test"], cwd=MOBILE_DIR)


def check_all():
    """Run full test and integration verification."""
    print("=== 1. Testing Engine ===")
    test_engine()
    print("\n=== 2. Testing Bank Generation ===")
    generate_banks(seeds=[7, 42], n=2)
    print("\n=== Verification Successful! ===")


def main():
    parser = argparse.ArgumentParser(description="exam-prep monorepo runner")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    subparsers.add_parser("test-engine", help="Run pytest on engine/")
    subparsers.add_parser("test-mobile", help="Run flutter test on mobile/")
    subparsers.add_parser("check", help="Run engine tests and bank generation check")

    gen_parser = subparsers.add_parser("generate-banks", help="Generate question bank JSON assets")
    gen_parser.add_argument("--seeds", type=int, nargs="+", default=[7, 42], help="Random seeds")
    gen_parser.add_argument("--n", type=int, default=10, help="Questions per topic")

    args = parser.parse_args()

    if args.command == "test-engine":
        test_engine()
    elif args.command == "generate-banks":
        generate_banks(args.seeds, args.n)
    elif args.command == "test-mobile":
        test_mobile()
    elif args.command == "check" or args.command is None:
        check_all()


if __name__ == "__main__":
    main()
