# Question Schema v1

The JSON contract every quiz UI implements against. Also available
programmatically via `fs_quiz.interop.flutter_contract()`.

## Bank file

```jsonc
{
  "schema_version": 1,
  "generator": "fs-exam-prep",
  "engine_version": "0.1.0",
  "question_count": 120,
  "questions": [ /* question objects */ ]
}
```

## Question object

| Field | Type | Meaning |
|---|---|---|
| `qid` | string | Stable 12-hex id: `sha1(generator:seed:index)[:12]` |
| `schema_version` | int | Must equal the engine's `SCHEMA_VERSION` |
| `domain` | string | One of the 7 FS knowledge-area slugs (see below) |
| `topic` | string | Generator topic slug, e.g. `traverse-misclosure` |
| `difficulty` | int | 1 = recall/one-step, 2 = multi-step, 3 = exam-hard |
| `stem` | string | Question text, plain text (no HTML) |
| `choices` | string[4] | Exactly 4 unique answer strings |
| `answer_index` | int | 0–3, index of the correct choice |
| `explanation` | string | Worked solution using the question's own numbers |
| `parameters` | object | The randomized inputs (allows re-derivation / auditing) |
| `seed` | int | Master seed used for this question |

## Domain slugs

```
surveying-processes-and-methods
mapping-processes-and-methods
boundary-law-and-real-property
surveying-principles-geodesy
survey-computations
business-concepts-ethics
applied-math-statistics
```

## Grading

Client-side: `selected_index == answer_index`. No partial credit in v1.

## Versioning policy

- Patch/minor engine releases never change this schema.
- A schema change bumps `schema_version`; old banks keep working with old
  engines, and `import_bank` fails loudly on mismatch instead of silently
  misgrading.
