"""Send each note five times to the model that the extractor calls, with the same prompt:

    python3 send_five.py 0147 0104

The prompt is prompt.txt. Each note is notes/<number>.txt. The script sends no schema. It calls
the model through model.py, one call for each reply. It saves each reply as it came, in
replies/prompt-<code>/<number>-1.txt to <number>-5.txt. The code comes from the text of
prompt.txt, so a changed prompt gets a new folder. The script asks the model for each reply once.
When the folder holds a reply already, the script does not ask for it again. Last, it writes each
note, the dates and numbers that it has, and its five replies, field by field, in field-by-field.txt.
It prints one line for each note.
"""
import hashlib
import json
import pathlib
import re
import sys
import textwrap

HERE = pathlib.Path(__file__).resolve().parent
FIELDS = ["tax_year", "form", "issue", "amount_in_question", "next_action"]
RUNS = 5
NO_JSON = "(no JSON in this reply)"
NO_VALUE = "(no value)"
TABLE = "field-by-field.txt"


def reply_folder(lab):
    """The folder for the replies to the prompt in lab/prompt.txt."""
    prompt = (lab / "prompt.txt").read_text().replace("\r\n", "\n")
    return lab / "replies" / ("prompt-" + hashlib.sha256(prompt.encode()).hexdigest()[:8])


def reply_files(lab, note):
    return [reply_folder(lab) / f"{note}-{run}.txt" for run in range(1, RUNS + 1)]


def read_reply(text):
    """The JSON object in one reply, or None when the reply holds no JSON object."""
    text = text.strip()
    tries = [text]
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    if fenced:
        tries.append(fenced.group(1))
    braces = re.search(r"\{.*\}", text, re.S)
    if braces:
        tries.append(braces.group(0))
    for candidate in tries:
        try:
            found = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(found, dict):
            return found
    return None


def shown(reply, field):
    """A value as JSON: text in quotes, a number and null without."""
    if reply is None:
        return NO_JSON
    if field not in reply:
        return NO_VALUE
    return json.dumps(reply[field], ensure_ascii=False)


def dates_and_numbers(text):
    """The dates and the numbers in a text, each once, in their order. A number loses its commas: 18,400 is 18400."""
    found = re.findall(r"\d{4}-\d{2}-\d{2}|\d+(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?", text)
    return list(dict.fromkeys(item.replace(",", "") for item in found))


def show(lab, note):
    """The five replies to one note, field by field, as lines of text, and the marks for a missing value in them."""
    replies = [read_reply(path.read_text()) for path in reply_files(lab, note)]
    text = (lab / "notes" / f"{note}.txt").read_text().strip()
    lines = ["", f"Note {note} says: {text}",
             f"The dates and numbers that the note has: {', '.join(dates_and_numbers(text)) or 'none'}.",
             "Its five replies, field by field:"]
    marks = set()
    for field in FIELDS:
        values = [shown(reply, field) for reply in replies]
        distinct = list(dict.fromkeys(values))
        same = "the same in all five" if len(distinct) == 1 else f"{len(distinct)} different values"
        lines.append(f"  {field}: {same}")
        for value in distinct:
            which = [str(run) for run, v in enumerate(values, start=1) if v == value]
            lines.append(f"    {'replies' if len(which) > 1 else 'reply'} {', '.join(which)}: {value}")
        marks |= {v for v in values if v in (NO_JSON, NO_VALUE)}
    return lines, marks


def main():
    notes = sys.argv[1:]
    if not notes or not all(re.fullmatch(r"\d{4}", n) and (HERE / "notes" / f"{n}.txt").is_file() for n in notes):
        sys.exit("Usage: python3 send_five.py 0147 0104. Each number names a note in notes/.")
    folder = reply_folder(HERE)
    to_send = [(note, path) for note in notes for path in reply_files(HERE, note) if not path.is_file()]
    if to_send:
        from model import ask  # the lab's route to the model, model.py

        prompt = (HERE / "prompt.txt").read_text()
        folder.mkdir(parents=True, exist_ok=True)
    else:
        print(f"{folder.relative_to(HERE)}/ holds all the replies already. This run sends nothing.")
    # One line for each note: the number of each reply when the script saves it, or at once if an earlier run
    # saved it.
    for note in notes:
        print(f"Note {note}: reply", end="", flush=True)
        for path in reply_files(HERE, note):
            if not path.is_file():
                try:
                    reply = ask(prompt, (HERE / "notes" / f"{note}.txt").read_text())
                except Exception as failure:  # the script reports any failure of the route, and stops
                    print(flush=True)  # ends the line of replies saved so far
                    sys.exit(f"The model did not reply ({failure}). Run the send again: cell 2, or python3 "
                             f"send_five.py {' '.join(notes)}. It asks only for the replies that are missing. If it "
                             "stops again, tell your trainer. To continue without the model, use the replies of the "
                             "course's run of 2026-10-20. In a terminal in lab, or with ! in a new cell, run: cp "
                             f"../../answers/same-note-five-times/replies/*.txt {folder.relative_to(HERE)}/. Then "
                             f"run cell 2 again, or python3 send_five.py {' '.join(notes)}. It sends nothing, and "
                             f"writes {TABLE}.")
                path.write_text(reply)
            print(f" {path.stem.split('-')[1]}", end="", flush=True)
        print(" saved.", flush=True)
    lines = ["Text is in quotes. A number and null have no quotes."]
    marks = set()
    for note in notes:
        shown_lines, shown_marks = show(HERE, note)
        lines += shown_lines
        marks |= shown_marks
    if marks:
        lines.append("")
        if NO_JSON in marks:
            lines.append(f"{NO_JSON}: the reply holds no JSON object, so it gives no values.")
        if NO_VALUE in marks:
            lines.append(f"{NO_VALUE}: the reply holds no such field.")
        lines.append("For such a reply, you can write its number in the row or not. The check accepts both.")
    # Each long line goes on over more lines, so the editor shows all of it without a scroll to the side.
    wrapped = [textwrap.fill(line, 90, subsequent_indent=" " * (len(line) - len(line.lstrip()) + 2),
                             break_long_words=False, break_on_hyphens=False) for line in lines]
    (HERE / TABLE).write_text("\n".join(wrapped) + "\n")
    print(f"{TABLE} shows the five values of each field, beside each note.")


if __name__ == "__main__":
    main()
