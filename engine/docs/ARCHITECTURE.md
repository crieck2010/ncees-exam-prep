# Architecture

`fs-exam-prep` is a pure-Python **question-bank engine** for the NCEES FS exam.
It turns a (domain, topic, count, seed) into reproducible, parameterized
practice questions serialized as versioned JSON. It does no rendering, no
network I/O, and no scheduling — quiz UIs (CLI today, Streamlit/Flutter
tomorrow) consume the JSON banks.

This mirrors the suite convention (cf. `survey-currents`): a stdlib-only
engine core, a thin UI layer, duck-typed interop, and a versioned artifact
contract.

## Module map

```
src/fs_quiz/
    schema.py       Question dataclass + SCHEMA_VERSION. The interop contract.
                    Frozen, JSON-serializable, validated on construction.
    registry.py     @register(domain, topic) decorator + discovery.
                    Single source of truth for "what can we generate".
    engine.py       QuizEngine: generate / generate_bank / export_bank /
                    import_bank / grade. Deterministic replay from seed.
    generators/
        __init__.py           Imports domain modules so they self-register.
        survey_computations.py  Phase 1: 12 parameterized generators.
    interop.py      Duck-typed bridges: flutter_contract(), to/from_jsonl.
                    Never imports a sibling package.
    cli.py          Thin CLI: list-domains / generate / quiz. No math here.
```

## Data flow

```
(seed, domain, topic, n)
        |
        v
  QuizEngine.generate() --rng--> generator(rng, qid) --> Question
        |                                                (frozen dataclass)
        v
  export_bank() --> bank.json (schema_version, questions[])
        |
        +--> CLI quiz / Streamlit / Flutter app (reads JSON only)
```

## Key invariants

1. **Determinism.** Identical (generator, seed, index) always yields the
   identical question, byte-for-byte. `qid = sha1(generator:seed:index)[:12]`.
2. **Schema versioning.** `Question` rejects unknown `schema_version`;
   `import_bank` rejects banks from a different schema. Bump `SCHEMA_VERSION`
   only with a migration note in the CHANGELOG.
3. **Distractors teach.** Every wrong choice is a classic exam mistake
   (back-azimuth, sin/cos swap, forgotten 1/2, ...), and `explanation` works
   the solution with the question's own numbers.
4. **No sibling imports.** `interop.py` exposes the Flutter contract as data;
   the app implements against JSON, never against this package.
5. **Original content only.** Generators synthesize fresh numbers every run;
   no NCEES or review-manual items are reproduced.

## Scaling notes

- Generation is embarrassingly parallel: shard by (topic, seed) across
  processes; qids stay globally unique by construction.
- Banks are plain JSON/JSONL — cache them in the app bundle, a CDN, or
  SQLite; the engine never needs to run on-device.
- Adding a domain = one new module under `generators/` + one import line.
  See `docs/ADDING_A_DOMAIN.md`.
