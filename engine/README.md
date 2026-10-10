# fs-exam-prep

**A parameterized question-bank engine for the NCEES FS exam — infinite,
seeded, reproducible practice questions for all 7 FS knowledge areas.**

**v1.0.0 — schema v1 locked.** The question-bank contract is frozen and
machine-enforced (see `docs/SCHEMA_CONTRACT.md`): the Flutter app and any
other consumer can build against `schema/question-v1.json` with confidence
that v1 banks will always parse.

Instead of a static list of 200 stale questions, `fs-exam-prep` *generates*
questions: each generator randomizes its numbers from a seed, so the bank is
effectively infinite and every practice run is fresh. Same seed replays
byte-identical — share a seed, share an exam.

This repo is the **engine** of the FS Exam Prep Quiz App program. Thin quiz
UIs (CLI today, Flutter iOS/Android app tomorrow) consume versioned JSON
question banks the engine produces. Engine-first, like every suite module:
pure Python, stdlib-only, zero UI imports.

## Status

**Phase 1 — engine: COMPLETE (v1.0.0).** All 7 FS domains shipped — 48 generators,
172 tests passing — and schema v1 is locked and machine-enforced
(`docs/SCHEMA_CONTRACT.md`). Phase 2 (Flutter app) and Phase 3 (freemium +
AdMob monetization) are tracked on the
[FS Exam Prep Quiz App project board](https://github.com/users/crieck2010/projects).

## The 7 FS domains

| Domain | Generators | Status |
|---|---|---|
| `survey-computations` | inverse, forward, traverse-misclosure, bowditch, area-coordinates, horizontal-curve, vertical-curve, level-notes, stadia, volumes, error-propagation, angular-misclosure | ✅ v0.1.0 |
| `boundary-law-and-real-property` | hierarchy-of-calls, senior-junior-rights, plss, water-boundaries, easements, adverse-possession, deeds-recording | ✅ v0.2.0 |
| `surveying-processes-and-methods` | error-types, edm-ppm, three-wire, curvature-refraction, gnss-window, traverse-types, accuracy-precision | ✅ v0.3.0 |
| `mapping-processes-and-methods` | photo-scale, contour-interpolation, utm-zone, raster-vector, lidar-products, state-plane-projection | ✅ v0.3.0 |
| `surveying-principles-geodesy` | orthometric-height, combined-factor, elevation-factor, datums, grid-vs-ground | ✅ v0.3.0 |
| `business-concepts-ethics` | duty-hierarchy, sealing, contract-elements, fee-structures, conflict-of-interest | ✅ v0.3.0 |
| `applied-math-statistics` | law-of-sines, law-of-cosines, std-error-mean, confidence-intervals, significant-figures, unit-conversions | ✅ v0.3.0 |

## Install

```bash
pip install fs-exam-prep            # engine core (stdlib only)
pip install "fs-exam-prep[dev]"    # + pytest
```

Or from source:

```bash
git clone https://github.com/crieck2010/fs-exam-prep
cd fs-exam-prep && pip install -e ".[dev]"
```

## Quickstart

```bash
# what can we generate?
fs-quiz list-domains

# build a 120-question bank (12 topics x 10) for survey computations
fs-quiz generate --domain survey-computations --topic inverse --n 10 --seed 42 --out bank.json

# take the quiz in your terminal
fs-quiz quiz --bank bank.json
```

```python
from fs_quiz.engine import QuizEngine

eng = QuizEngine()
bank = eng.generate("survey-computations", "traverse-misclosure", n=20, seed=7)
eng.export_bank(bank, "bank.json")          # ship this file with the app

questions = eng.import_bank("bank.json")
summary = eng.grade(questions, {q.qid: 0 for q in questions})
print(summary["score_pct"])
```

## Architecture

- `src/fs_quiz/schema.py` — versioned `Question` dataclass (the interop contract)
- `src/fs_quiz/registry.py` — `@register(domain, topic)` generator discovery
- `src/fs_quiz/engine.py` — deterministic generation, bank import/export, grading
- `src/fs_quiz/generators/` — one module per FS domain (12 generators shipped)
- `src/fs_quiz/interop.py` — duck-typed bridges incl. the Flutter JSON contract
- `src/fs_quiz/cli.py` — thin CLI (`fs-quiz`)

Full details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) ·
[docs/QUESTION_SCHEMA.md](docs/QUESTION_SCHEMA.md) ·
[docs/INTEROP.md](docs/INTEROP.md).

## Why generated, not static

| Static bank | This engine |
|---|---|
| 200 questions, memorized in a week | Infinite — new numbers every seed |
| One answer key to leak | Seeds are the key; fresh exam every run |
| Manual authoring per question | 12 generators cover a whole domain |
| Stale after one spec change | Regenerate with new parameters |

## Roadmap

- **v1.0.0** ✅ — schema v1 locked; engine API stable
- **Phase 2** — Flutter app (iOS + Android) consuming bank JSON
- **Phase 3** — freemium (free daily quota + ads) + one-time unlock

## Contributing

New domains follow [docs/ADDING_A_DOMAIN.md](docs/ADDING_A_DOMAIN.md):
one module, registered topics, independent-recomputation tests, original
content only (never reproduce NCEES or publisher items).

## License

MIT — see [LICENSE](LICENSE).
