"""A wrong run 2, for check.py. It is the extractor of the course's run 2, lab-states/run2/extractor.py,
with one change: check_reply does not check a reply against the output schema. So the extractor
accepts each reply that is JSON, and the run 2 test test_reply_missing_amount_is_a_failure fails.
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
    problems = []  # The one change: no check against the schema.
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
