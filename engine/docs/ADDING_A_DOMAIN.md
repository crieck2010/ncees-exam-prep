# Adding a Domain

Checklist for adding one of the remaining 6 FS knowledge areas
(or any new question source). Follow it exactly; the tests enforce the rest.

1. **Create the module**: `src/fs_quiz/generators/<domain_slug>.py`,
   with `DOMAIN = "<domain_slug>"` matching `schema.DOMAIN` slugs.
2. **Write generators**: each is `def gen_<name>(rng, qid) -> Question`,
   decorated with `@register(DOMAIN, "<topic-slug>")`.
   - Randomize with `rng` only (never the global `random` module).
   - Build choices with the `_mcq`-style helper: exactly 4 unique strings.
   - Make every distractor a *plausible exam mistake*, not a random number.
   - Put the randomized inputs in `parameters` so answers stay auditable.
   - Write `explanation` as a worked solution with the actual numbers.
3. **Register the import**: add the module to
   `src/fs_quiz/generators/__init__.py` and to the import block in
   `engine.py`.
4. **Tests**: add `tests/test_<domain_slug>.py` with, per topic:
   - independent recomputation of the answer from `parameters`
     (see `test_survey_computations.py::_recompute` — copy the pattern),
   - determinism (same seed replays byte-identical),
   - choice uniqueness.
   Update `EXPECTED_*_TOPICS` in `test_registry.py`.
5. **Docs**: add the topic list to `README.md`'s domain table.
6. **Version**: bump minor in `pyproject.toml` + `CHANGELOG.md`
   (new domain = new capability, not a patch).

## Content rules (non-negotiable)

- All questions are **original**. Never reproduce NCEES, review-manual, or
  publisher items — paraphrased or otherwise.
- Keep units in the stem. Keep numbers exam-realistic (no 0.0001-ft traps).
- Difficulty honestly: 1 = one formula, 2 = two steps, 3 = full exam style.
