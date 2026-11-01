"""Count the failures in the replies: python3 count_failures.py

Each file in replies/ holds one reply for the note with the same number in notes/. Replies 0102
and 0147 are the lab's recorded replies, from tests/recorded/. The other six are hand-written,
each to show a failure. This script gives each reply to check_reply in extractor.py. It shows
whether each reply passes, and the reason for each failure. It calls no model.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
try:
    from extractor import ExtractionFailed, check_reply
except Exception as error:  # the script shows an edit that stops extractor.py loading
    where = ("Python cannot read schema/output.schema.json as JSON" if type(error).__name__ == "JSONDecodeError"
             else "extractor.py does not load")
    sys.exit(f"{where}. Python shows {type(error).__name__}: {error}")

replies = sorted((ROOT / "replies").glob("*.txt"))
failures = 0
for path in replies:
    name = path.relative_to(ROOT).as_posix()
    try:
        check_reply(path.read_text())
    except ExtractionFailed as failure:
        failures += 1
        print(f"{name}  failure: {failure}")
    except Exception as error:
        print(f"{name}  check_reply stops with {type(error).__name__}: {error}")
    else:
        print(f"{name}  passes")
print(f"Failures: {failures} of {len(replies)} replies.")
