# Changelog

## v1.0.0 — 2026-10-09
- **Schema v1 locked** (see `docs/SCHEMA_CONTRACT.md`): machine-readable
  `schema/question-v1.json`, stdlib-only `contract.py` validator, and a frozen
  96-question golden fixture — any future breaking change fails tests loudly
  instead of shipping silently.
- `import_bank` now validates the full v1 contract (fields, types, unique
  choices, unique qids, count consistency); new `fs-quiz validate` command
  for the app build pipeline.
- Hardening: 60-seed sweep across all 48 topics with zero distractor
  collisions; fixed 3 latent generator bugs found by the fuzz test
  (bowditch, error-propagation, edm-ppm distractor collisions).
- 172 tests passing.

## v0.3.0 — 2026-10-08
- All 7 FS domains shipped (48 generators total): `surveying-processes-and-methods`
  (7), `mapping-processes-and-methods` (6), `surveying-principles-geodesy` (5),
  `business-concepts-ethics` (5), `applied-math-statistics` (6).
- Mixed-domain bank generation across the full blueprint
  (`fs-quiz generate --all`).
- 164 tests passing; every new answer independently re-derived in tests
  (caught 3 more generator bugs pre-release: duplicate distractors,
  identical distractor pair).

## v0.2.0 — 2026-10-08
- New domain: `boundary-law-and-real-property` with 7 scenario generators
  (hierarchy-of-calls, senior-junior-rights, plss, water-boundaries, easements,
  adverse-possession, deeds-recording).
- Scenario templates with randomized names/dates/measurements; answers
  re-derivable from question parameters (tests re-derive every answer
  independently, including an independent PLSS boustrophedon implementation).
- 75 tests passing (52 from v0.1.0 + 23 new).

## v0.1.0 — 2026-10-08
- Initial release: `survey-computations` domain with 12 parameterized generators
  (inverse, forward, traverse-misclosure, bowditch, area-coordinates,
  horizontal-curve, vertical-curve, level-notes, stadia, volumes,
  error-propagation, angular-misclosure).
- Versioned Question schema (v1), generator registry, deterministic QuizEngine
  (generate / bank / export / import / grade), thin `fs-quiz` CLI.
- Duck-typed interop: `flutter_contract()` JSON contract for the Phase 2 app.
- 52 tests passing (schema, registry, per-topic independent recomputation,
  determinism, engine round-trip).
- Docs: ARCHITECTURE, QUESTION_SCHEMA, INTEROP, ADDING_A_DOMAIN.
