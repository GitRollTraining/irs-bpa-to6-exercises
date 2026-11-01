"""The case-notes extractor: one note in, its five fields out, checked against the output schema.

    python3 extractor.py notes/0147.txt

prints the fields as JSON, or the reason the model's reply failed its check. The model is reached
through model.py; the tests pass in a recorded reply instead, so they never call the model. A reply
that fails its check is reported as a failure and never repaired.
"""
import json
import pathlib
import sys

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "schema" / "output.schema.json").read_text())
SYSTEM_PROMPT = (ROOT / "prompts" / "system.txt").read_text()


class ExtractionFailed(Exception):
    """The model's reply was not JSON that matches the output schema."""


def check_reply(reply_text):
    try:
        fields = json.loads(reply_text)
    except json.JSONDecodeError as err:
        raise ExtractionFailed(f"the reply is not JSON ({err.msg})") from None
    # The model sometimes writes the amount as text, such as "None stated" or "18,400".
    # Keep the digits of the text, or use null when it has none. Then fewer replies fail.
    amount = fields.get("amount_in_question")
    if isinstance(amount, str):
        digits = "".join(c for c in amount if c.isdigit())
        fields["amount_in_question"] = int(digits) if digits else None
    problems = [error.message for error in jsonschema.Draft202012Validator(SCHEMA).iter_errors(fields)]
    if problems:
        raise ExtractionFailed("; ".join(problems))
    return fields


def extract(note_text, ask=None):
    if ask is None:
        from model import ask
    reply = ask(SYSTEM_PROMPT, f"<note>{note_text.strip()}</note>", SCHEMA)
    return check_reply(reply)


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 extractor.py NOTE_FILE")
    try:
        print(json.dumps(extract(pathlib.Path(sys.argv[1]).read_text())))
    except ExtractionFailed as failure:
        sys.exit(f"Failed: {failure}")


if __name__ == "__main__":
    main()
