"""Checks schema/extraction.schema.json against hand-written outputs. No model is called and no
note is read: every output here is written out in the test itself."""
import json
import pathlib

import pytest
from jsonschema import Draft202012Validator

SCHEMA_PATH = pathlib.Path(__file__).resolve().parent.parent / "schema" / "extraction.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())
VALIDATOR = Draft202012Validator(SCHEMA)

# The result docs/fields.md gives for note 0147.
NOTE_0147 = {
    "tax_year": 2023,
    "form": "1040",
    "issue": "Schedule C gross receipts below information returns",
    "amount_in_question": 18400,
    "next_action": "Follow up on records request in 30 days",
}


def errors(output):
    return [e.message for e in VALIDATOR.iter_errors(output)]


def changed(**fields):
    return {**NOTE_0147, **fields}


def without(field):
    return {k: v for k, v in NOTE_0147.items() if k != field}


def test_schema_is_valid_2020_12():
    Draft202012Validator.check_schema(SCHEMA)


def test_schema_names_exactly_the_five_fields():
    fields = ["tax_year", "form", "issue", "amount_in_question", "next_action"]
    assert sorted(SCHEMA["properties"]) == sorted(fields)
    assert sorted(SCHEMA["required"]) == sorted(fields)
    assert SCHEMA["additionalProperties"] is False


def test_documented_0147_result_passes():
    assert errors(NOTE_0147) == []


def test_null_amount_passes():
    assert errors(changed(amount_in_question=None)) == []


def test_missing_amount_fails():
    assert errors(without("amount_in_question"))


@pytest.mark.parametrize("field", ["tax_year", "form", "issue", "next_action"])
def test_each_other_field_is_required(field):
    assert errors(without(field))


def test_extra_field_fails():
    assert errors(changed(confidence=0.9))


@pytest.mark.parametrize("bad", [
    {"tax_year": "2023"},
    {"tax_year": 2023.5},
    {"tax_year": None},
    {"form": 1040},
    {"issue": None},
    {"next_action": ["Follow up"]},
    {"amount_in_question": "18,400"},
    {"amount_in_question": 18400.5},
    {"amount_in_question": True},
])
def test_wrong_types_fail(bad):
    assert errors(changed(**bad))
