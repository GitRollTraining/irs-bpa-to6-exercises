"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads what is in lab/: your rows in record.md, and the replies that send_five.py saved for the
prompt in prompt.txt. It calls no model.

It reads two rows, as the table in step 3 gives them. Each names the replies whose value the note
does not state. The check reads the five values of that field in your own replies, beside the note.
- note 0147, next_action: a value with a date or a number that the note does not have must be in
  the row. A value that is only the note's own words and numbers, in its order, must not be. Each
  other value, such as one with new words only, can be in the row or not.
- note 0104, amount_in_question: the note names no amount, so each value that is not null must be
  in the row, and null must not.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE / "lab"
sys.path.insert(0, str(HERE / "files"))
from send_five import FIELDS, RUNS, read_reply, reply_files  # noqa: E402  (no model call)

NOTES = ["0147", "0104"]
ROWS = {"0147": ["next_action"], "0104": ["amount_in_question"]}  # the two rows of record.md, step 3
# What each note states for the fields with one right value: its year, its form, and its amount.
# None: the note names no amount, so null belongs in amount_in_question.
STATED = {"0147": {"tax_year": 2023, "form": 1040, "amount_in_question": 18400},
          "0104": {"tax_year": 2023, "form": 1040, "amount_in_question": None}}
NO_VALUE = object()  # the reply holds no JSON object, or no such field
# The line of section 2.1 that each line of the table in step 3 rests on, as its Why column quotes it.
FLUENT = 'Section 2.1: "A fluent answer is not a known answer."'
NULL = 'Section 2.1, under that heading: "text where null belongs".'
RESET = "python3 ~/practice/reset.py same-note-five-times"
SEND = "Send them: run cell 2, or python3 send_five.py 0147 0104."


def tokens(value):
    """The words and the numbers of a value, in their order and in lower case.

    One amount has one number: 18,400 and 18400.00 and 18.4k are 18400. $ is the word dollar.
    """
    text = value if isinstance(value, str) else json.dumps(value)
    text = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", text)
    text = re.sub(r"(\d+(?:\.\d+)?)(?:k|K)\b|(\d+(?:\.\d+)?)\s+thousand\b",
                  lambda m: str(round(float(m.group(1) or m.group(2)) * 1000)), text)
    text = re.sub(r"(?<=\d)\.0+(?!\d)", "", text)
    return re.findall(r"[a-z]+|\d+", text.replace("$", " dollar ").lower())


def split(found):
    """The words and the numbers of a list of tokens, as two sets."""
    return {t for t in found if not t.isdigit()}, {int(t) for t in found if t.isdigit()}


def in_order(found, note):
    """True when the tokens are a stretch of the note: each three in a row are three in a row in the note."""
    if not found:
        return False
    size = min(3, len(found))
    runs = {tuple(note[i:i + size]) for i in range(len(note) - size + 1)}
    return all(tuple(found[i:i + size]) in runs for i in range(len(found) - size + 1))


def kind(note, field, value, note_tokens):
    """'not stated', 'stated', or 'either', when the rules allow both answers."""
    if value is NO_VALUE:
        return "either"
    if field in STATED[note] and STATED[note][field] is None:  # an amount where the note names none
        return "stated" if value is None else "not stated"
    if value is None:  # null, where the note gives a value: the row can name it or not
        return "either"
    found = tokens(value)
    numbers = split(found)[1]
    if not numbers <= split(note_tokens)[1]:  # a number or a date that the note does not give
        return "not stated"
    if field in STATED[note] and STATED[note][field] not in numbers:  # "Schedule C" as the form, or 30 as the amount
        return "either"  # the note's words or numbers, in another field: the same
    return "stated" if in_order(found, note_tokens) else "either"  # new words or a new order: the same


def named(cell):
    """The replies that a cell names, as a set. None for an empty cell. 'unclear' when the cell names no reply."""
    text = cell.lower()
    if not re.search(r"[a-z0-9]", text):
        return None
    # A reply number stands alone: not part of a longer number, such as a date or 2.5.
    picked = {int(d) for d in re.findall(r"(?<!\d)(?<!\d\.)[1-5](?!\d|\.\d)", text)}
    for first, last in re.findall(r"(?<!\d)(?<!\d\.)([1-5])\s*(?:-|–|to)\s*([1-5])(?!\d|\.\d)", text):
        picked |= set(range(int(first), int(last) + 1))
    words = re.findall(r"[a-z]+", text)
    if not picked and "none" in words:  # "none, all five give null" names no reply
        return set()
    if "all" in words:
        picked |= set(range(1, RUNS + 1))
    if not picked:
        return "unclear"
    return picked


def rows(text):
    """{(note, field): its Replies cell}, from the table in record.md."""
    found = {}
    for line in text.splitlines():
        if line.strip().startswith("|"):
            cells = [cell.strip().strip("`*").strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0] in NOTES and cells[1] in FIELDS:
                found[(cells[0], cells[1])] = " ".join(cells[2:])
    return found


def count(n, thing):
    """'1 reply number', '2 reply numbers'."""
    return f"{n} {thing}" + ("" if n == 1 else "s")


def stop(message):
    print("Not yet: 1 left.")
    print("- " + message)
    sys.exit(1)


if not (LAB / ".git").is_dir():
    stop(f"there is no repository lab/ yet. Run {RESET}.")
for name in ("record.md", "prompt.txt"):
    if not (LAB / name).is_file():
        stop(f"{name} is missing. Run {RESET} to get it again. The reset also removes your record and replies.")

problems = []
table = rows((LAB / "record.md").read_text())
accepted = 0
for note in NOTES:
    note_file = LAB / "notes" / f"{note}.txt"
    if not note_file.is_file():
        problems.append(f"notes/{note}.txt is missing. Run {RESET} to get it again. "
                        "The reset also removes your record and replies.")
        continue
    paths = reply_files(LAB, note)
    sent = all(path.is_file() for path in paths)
    if not sent:
        problems.append(f"replies/ does not hold five replies to note {note} for the prompt in prompt.txt. {SEND}")
    replies = [read_reply(path.read_text()) for path in paths] if sent else []
    note_tokens = tokens(note_file.read_text())
    empty = []
    for field in ROWS[note]:
        cell = table.get((note, field))
        if cell is None:
            problems.append(f"record.md: the table has no row for note {note}, {field}. Add the row again, "
                            "in the form of the other rows.")
            continue
        answer = named(cell)
        if answer is None:
            empty.append(field)
            continue
        if answer == "unclear":
            problems.append(f"record.md, note {note}, {field}: write the reply numbers, 1 to 5. 2, 4 means "
                            "replies 2 and 4. none means no reply.")
            continue
        if not sent:
            continue
        values = [reply.get(field, NO_VALUE) if reply is not None else NO_VALUE for reply in replies]
        kinds = {run: kind(note, field, value, note_tokens) for run, value in enumerate(values, start=1)}
        left_out = len([run for run in kinds if kinds[run] == "not stated" and run not in answer])
        put_in = len([run for run in kinds if kinds[run] == "stated" and run in answer])
        if not left_out and not put_in:
            accepted += 1
            continue
        no_amount = field == "amount_in_question" and STATED[note][field] is None
        say = []  # what the row lacks, and what it has too many of, in the words of the table in step 3
        if left_out and no_amount:
            say.append(f"note {note} names no amount, so write the number of each reply whose value is not null. "
                       f"The row lacks {count(left_out, 'reply number')}.")
        elif left_out:
            say.append(f"the row lacks {count(left_out, 'reply number')}. Find "
                       + ("the value" if left_out == 1 else f"the {left_out} values")
                       + " with a date or a number that the note does not have, in field-by-field.txt.")
        if put_in:
            one = put_in == 1
            say.append(f"you wrote {put_in} {'reply whose value is' if one else 'replies whose values are'} "
                       + ("null, the correct value here." if no_amount else "only the words and numbers of the note.")
                       + f" Take {'its number' if one else 'their numbers'} out.")
        # The line of section 2.1 that the row rests on, once: the Why column of the table in step 3.
        lines = [NULL if no_amount else FLUENT]
        problems.append(f"record.md, note {note}, {field}: " + " Also, ".join(say) + " " + " ".join(lines))
    if empty:
        row = f"row{'s' if len(empty) > 1 else ''} {', '.join(empty)}"
        problems.append(f"record.md, note {note}: fill in the {row}, as the table in step 3 says. "
                        "Write the reply numbers, 1 to 5. If no reply fits, write none."
                        + ("" if sent else " Do this after the send."))

if problems:
    print(f"Not yet: {len(problems)} left.")
    print("\n".join(f"- {p}" for p in problems))
    sys.exit(1)
print(f"Done: replies/ holds five replies to each note. The course accepts each of your {accepted} rows for these "
      "replies.")
