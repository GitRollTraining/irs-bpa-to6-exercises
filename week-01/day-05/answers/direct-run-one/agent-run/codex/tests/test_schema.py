import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError


SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schema" / "case_notes.schema.json")
    .read_text(encoding="utf-8")
)
VALIDATOR = Draft202012Validator(SCHEMA)


@pytest.fixture
def output():
    # Synthetic output: tests never read or log case notes or call a model.
    return {
        "tax_year": 2023,
        "form": "1040",
        "issue": "Example discrepancy",
        "amount_in_question": 1000,
        "next_action": "Request supporting records",
    }


def test_schema_is_valid():
    Draft202012Validator.check_schema(SCHEMA)


def test_integer_amount_passes(output):
    VALIDATOR.validate(output)


def test_null_amount_passes(output):
    output["amount_in_question"] = None
    VALIDATOR.validate(output)


@pytest.mark.parametrize("field", SCHEMA["required"])
def test_missing_field_fails(output, field):
    del output[field]
    with pytest.raises(ValidationError) as error:
        VALIDATOR.validate(output)
    assert error.value.validator == "required"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tax_year", "2023"),
        ("tax_year", 2023.5),
        ("tax_year", True),
        ("form", 1040),
        ("issue", None),
        ("next_action", []),
        ("amount_in_question", "1000"),
        ("amount_in_question", 1000.5),
        ("amount_in_question", True),
    ],
)
def test_wrong_type_fails(output, field, value):
    output[field] = value
    with pytest.raises(ValidationError) as error:
        VALIDATOR.validate(output)
    assert error.value.validator == "type"


def test_extra_field_fails(output):
    output["extra"] = "unexpected"
    with pytest.raises(ValidationError) as error:
        VALIDATOR.validate(output)
    assert error.value.validator == "additionalProperties"


@pytest.mark.parametrize("output", [None, [], "example", 42])
def test_non_object_fails(output):
    with pytest.raises(ValidationError) as error:
        VALIDATOR.validate(output)
    assert error.value.validator == "type"
