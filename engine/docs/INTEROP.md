# Interoperability

How `fs-exam-prep` plugs into quiz UIs and sibling engines. All bridges are
duck-typed — this package never imports a sibling, so install graphs stay
acyclic and every bridge is testable offline.

## Flutter app (Phase 2) — `interop.flutter_contract()`

The app never imports this package. It reads exported bank JSON files whose
shape is fully described by `flutter_contract()` (see
`docs/QUESTION_SCHEMA.md`). Build the app bundle like:

```bash
fs-quiz generate --all --n 25 --seed 20261008 --out assets/bank.json
```

Ship `assets/bank.json` with the app; grade client-side with
`selected_index == answer_index`. Regenerate the bundle per release with a
new seed for fresh questions.

## Streamlit study dashboard

```python
from fs_quiz.engine import QuizEngine
eng = QuizEngine()
bank = eng.import_bank("bank.json")   # or eng.generate_bank(...)
```

Render `stem`/`choices` with `st.radio`, grade with `eng.grade`, and show
`explanation` on misses. The engine stays importable with zero UI deps.

## survey-suite bridges (proposed)

- `survey-cogo`: computation generators could delegate their worked solutions
  to the suite's COGO functions as a cross-check (generator math vs. suite
  math must agree — a strong correctness property to test).
- `reel-studio` / content pipeline: "question of the day" Shorts can be
  rendered from bank JSON (`stem` + choices as kinetic text).

No changes were made to sibling repos. Proposed integrations only.
