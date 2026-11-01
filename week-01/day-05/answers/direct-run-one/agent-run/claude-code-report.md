I've added the output schema and its tests, and `pytest tests/test_schema.py` passes: 19 tests, all passing.

**What I added:**
- `schema/extraction.schema.json` is the schema for one extractor output. It allows exactly the five fields in `docs/fields.md`, all required, and rejects any extra field. `tax_year` must be an integer. `form`, `issue` and `next_action` must be strings. `amount_in_question` must be an integer or null, and must always be present.
- `tests/test_schema.py` checks outputs against that schema. It includes the two cases you asked for:
  - An output with `amount_in_question` missing **fails**.
  - An output with `amount_in_question: null` **passes**.

  It also checks that:
  - the schema itself is valid;
  - the documented result for note 0147 passes;
  - removing any of the other fields fails;
  - an extra field fails;
  - wrong types fail. Examples are `"2023"` as a year, `"18,400"`, `18400.5` or `true` as an amount, and `1040` as a number instead of a string.

**Your constraints:**
- No model is called; the tests never import `model.py`.
- Only `schema/` and `tests/` were changed.
- The tests don't read the note files, so no note text is logged. Every test output is written out in the test file, based on the 0147 result given in `docs/fields.md`.

**Things to know:**
- The tests use the `jsonschema` package, which was already installed here. If another machine doesn't have it, it needs to be installed there.
- My first command, which listed the repo and read the docs in one go, was blocked by the permission check. I read the same files individually instead, so nothing was skipped.
- Nothing is committed yet.