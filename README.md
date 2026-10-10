# NCEES Exam Prep

[![CI](https://github.com/crieck2010/ncees-exam-prep/actions/workflows/ci.yml/badge.svg)](https://github.com/crieck2010/ncees-exam-prep/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flutter](https://img.shields.io/badge/flutter-3.24%2B-02569B.svg)](https://flutter.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**An infinite, parameterized practice question engine and cross-platform mobile study app for professional licensing exams.**

Starting with the **NCEES Fundamentals of Surveying (FS)** exam, this repository serves as the flagship foundation for a planned family of mobile training apps covering:
- **NCEES FS** (Fundamentals of Surveying)
- **NCEES PS** (Principles and Practice of Surveying)
- **NCEES FE** (Fundamentals of Engineering - Civil & Other Disciplines)
- **NCEES PE** (Principles and Practice of Engineering)
- **State-Specific PLS** (Professional Land Surveyor legal & boundary exams)

---

## Architecture Overview

Instead of static question banks that are quickly memorized, this ecosystem utilizes a **two-tier architecture**:

```
+-------------------------------------------------------------+
|               Python Question Engine (engine/)              |
|  - 48 parameterized generators across 7 NCEES domains       |
|  - Deterministic seeds (seed 42, 7 -> infinite fresh exams) |
|  - Standard library only (zero runtime dependencies)        |
+-------------------------------------------------------------+
                              |
                schema/question-v1.json contract
                              |
                              v
+-------------------------------------------------------------+
|               Mobile Application (mobile/)                  |
|  - Cross-platform Flutter app for iOS & Android             |
|  - SM-2 Spaced Repetition (SRS) with confidence grading     |
|  - Question of the Day (QOTD), Streaks, & Exam Countdown    |
|  - Material 3 theming (persisted light/dark mode)           |
+-------------------------------------------------------------+
```

---

## Repository Structure

```
exam-prep/
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated Python & Flutter CI test pipeline
├── engine/                      # Phase 1: Pure Python question generator
│   ├── pyproject.toml           # Engine packaging config
│   ├── schema/                  # Machine-enforced question-v1.json schema
│   ├── src/fs_quiz/             # Generator registry & 7 domain implementations
│   ├── tests/                   # 172 unit & independent recomputation tests
│   └── docs/                    # Architecture, schema contract, and domain guides
└── mobile/                      # Phase 2: Flutter mobile quiz application
    ├── pubspec.yaml             # Flutter dependencies & metadata
    ├── lib/                     # Application source
    │   ├── core/                # Theming, notifications, monetization seam
    │   ├── data/                # Bank repository & schema validator
    │   └── features/            # Quiz session, SRS, streaks, QOTD, weekly reports
    ├── test/                    # 11 unit & widget test suites
    ├── assets/banks/            # Bundled seed-generated question banks
    └── tools/                   # Pipeline scripts (generate_banks.py)
```

---

## Quickstart

### 1. Python Engine

The engine generates deterministic, schema-validated question banks:

```bash
# Navigate to engine
cd engine

# Install in editable mode with test dependencies
pip install -e .
pip install pytest ruff

# Run 172 tests
pytest tests/ -v

# Generate a 120-question bank (12 topics x 10) for survey computations
fs-quiz generate --domain survey-computations --topic inverse --n 10 --seed 42 --out bank.json
```

### 2. Regenerating Mobile Question Banks

To produce fresh exams from any seed into the mobile app asset bundle:

```bash
python mobile/tools/generate_banks.py --n 10 --seeds 7 42 100
```

### 3. Flutter Mobile App

```bash
# Navigate to mobile
cd mobile

# Install dependencies
flutter pub get

# Run static analysis and unit tests
flutter analyze
flutter test

# Run on connected device or emulator
flutter run
```

---

## The 7 FS Knowledge Domains

| Domain | Generators | Status |
|---|---|---|
| **Survey Computations** | Inverse, forward, traverse misclosure, Bowditch, area by coordinates, horizontal curve, vertical curve, level notes, stadia, volumes, error propagation, angular misclosure | Complete |
| **Boundary Law & Real Property** | Hierarchy of calls, senior/junior rights, PLSS, water boundaries, easements, adverse possession, deeds & recording | Complete |
| **Surveying Processes & Methods** | Error types, EDM ppm, three-wire leveling, curvature & refraction, GNSS window, traverse types, accuracy vs. precision | Complete |
| **Mapping Processes & Methods** | Photo scale, contour interpolation, UTM zone, raster vs. vector, LiDAR products, state plane projection | Complete |
| **Principles & Geodesy** | Orthometric height, combined factor, elevation factor, datums, grid vs. ground | Complete |
| **Business Concepts & Ethics** | Duty hierarchy, professional sealing, contract elements, fee structures, conflict of interest | Complete |
| **Applied Math & Statistics** | Law of sines, law of cosines, standard error of the mean, confidence intervals, significant figures, unit conversions | Complete |

---

## Roadmap

- [x] **Phase 1: Question Bank Engine** — Complete (v1.0.0, 48 generators, 172 tests passing).
- [x] **Phase 2: Mobile UI Foundation** — Complete (v0.4.0, picker, quiz flow, SM-2 SRS, streaks, exam countdown).
- [ ] **Phase 3: Store Launch** — RevenueCat In-App Purchase integration, real app icons & splash screens, Google Play & Apple App Store submission.
- [ ] **Phase 4: Exam Family Expansion** — Generalize core into `exam-prep-engine` and `exam_prep_core` for PS, FE Civil, PE, and State PLS exams.

---

## License

MIT - see [LICENSE](LICENSE).
