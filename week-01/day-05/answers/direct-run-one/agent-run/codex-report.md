Added `schema/case_notes.schema.json` and `tests/test_schema.py`.

The schema requires exactly the five fields with the specified types. Tests verify that a missing `amount_in_question` fails and `null` passes.

`pytest tests/test_schema.py`: **22 passed**.

No model calls or note-text logging. Changes are limited to `schema/` and `tests/`.