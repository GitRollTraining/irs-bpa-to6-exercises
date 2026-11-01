"""Score the extractor's prompt on the labelled set. Run it from the top folder of the repository:

    python3 evaluation/score.py           scores the prompt in prompts/system.txt
    python3 evaluation/score.py --first   scores the first run, in evaluation/runs/1, with no model call

Each prompt gets its own run folder, evaluation/runs/<n>/. The folder keeps the prompt as it was
sent, one reply for each labelled note, and the score. For a note that has a reply for this prompt
and this schema, the scorer sends nothing. The extractor sends each other note to the model through
model.py, one call for each note.

The scorer compares tax_year, form and amount_in_question in each reply with the label of the note.
It prints the precision and the recall of each field. It saves the score, with each wrong value, as
score.txt in the run folder. A reply that is not JSON, or does not match the schema, counts as a
failure. The scorer never changes a reply. For the prompt of the first run, it sends nothing.
"""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
LABELS = ROOT / "evaluation" / "labels.jsonl"
RUNS = ROOT / "evaluation" / "runs"
PROMPT = ROOT / "prompts" / "system.txt"
SCHEMA = ROOT / "schema" / "output.schema.json"
FIELDS = ("tax_year", "form", "amount_in_question")


def fingerprint(prompt_text, schema_text):
    """A short code for one prompt with one schema. A change to either one gives a new code."""
    return hashlib.sha256((prompt_text + "\0" + schema_text).encode()).hexdigest()[:12]


def same_words(one, other):
    """True when two texts have the same words in the same order. Spaces and line breaks do not count."""
    return one.split() == other.split()


def load_labels(path=LABELS):
    """The labels, by note number: the five fields that each note should give."""
    labels = {}
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            label = json.loads(line)
            labels[str(label.pop("note"))] = label
        except (ValueError, KeyError, AttributeError, TypeError):
            sys.exit(f"{path.name}, line {number}: this line is not a label.")
    return labels


def runs(folder=RUNS):
    """Each run folder, by its number: (the folder, its record run.json)."""
    found = {}
    for record in folder.glob("*/run.json"):
        if record.parent.name.isdigit():
            found[int(record.parent.name)] = (record.parent, json.loads(record.read_text()))
    return dict(sorted(found.items()))


def replies_in(folder):
    """The replies in one run folder, by note number, as the model sent them."""
    return {path.stem: path.read_text() for path in folder.glob("*.txt") if path.stem.isdigit()}


def fields_of(reply_text, schema):
    """The fields of one reply. None when the reply fails its check: it is not JSON, or not as the schema says."""
    import jsonschema
    try:
        fields = json.loads(reply_text)
    except ValueError:
        return None
    if any(jsonschema.Draft202012Validator(schema).iter_errors(fields)):
        return None
    return fields


def score(labels, replies, schema):
    """For each field: the correct, extracted and expected values. Also each wrong value, and each failed reply."""
    counts = {field: {"correct": 0, "extracted": 0, "expected": 0} for field in FIELDS}
    wrong, failed = [], []
    for note in sorted(labels):
        label = labels[note]
        fields = fields_of(replies[note], schema) if note in replies else None
        if fields is None:
            failed.append(note)
        for field in FIELDS:
            if label[field] is not None:
                counts[field]["expected"] += 1
            if fields is None:
                continue
            if fields[field] is not None:
                counts[field]["extracted"] += 1
                if fields[field] == label[field]:
                    counts[field]["correct"] += 1
            if fields[field] != label[field]:
                wrong.append((note, field, label[field], fields[field]))
    return counts, wrong, failed


def ratio(part, whole):
    return f"{part / whole:.2f}" if whole else "n/a"


def report(number, labels, counts, wrong, failed):
    lines = [f"Run {number} of the set: {len(labels)} labelled notes. Replies that fail the schema: {len(failed)}.",
             "The scorer does not compare issue and next_action, which are phrases that a person reads.", "",
             f"{'field':<20}{'correct':>9}{'extracted':>11}{'expected':>10}{'precision':>11}{'recall':>8}"]
    for field in FIELDS:
        c = counts[field]
        lines.append(f"{field:<20}{c['correct']:>9}{c['extracted']:>11}{c['expected']:>10}"
                     f"{ratio(c['correct'], c['extracted']):>11}{ratio(c['correct'], c['expected']):>8}")
    lines += ["", "Wrong values (the note: its label, then the reply):"]
    for field in FIELDS:
        found = [(note, want, got) for note, name, want, got in wrong if name == field]
        if found:
            lines.append(f"  {field}, {len(found)} wrong:")
            lines += [f"    {note}: {json.dumps(want)}, then {json.dumps(got)}" for note, want, got in found]
    if failed:  # wrapped at 90 characters, as each line of score.txt is
        lines += textwrap.wrap("Replies that fail the schema: " + ", ".join(failed), 90, initial_indent="  ",
                               subsequent_indent="    ")
    if not wrong and not failed:
        lines.append("  none")
    return "\n".join(lines) + "\n"


def summary(counts):
    return ", ".join(f"{field} {ratio(counts[field]['correct'], counts[field]['extracted'])} "
                     f"{ratio(counts[field]['correct'], counts[field]['expected'])}" for field in FIELDS)


def new_run(number, code):
    """Make the folder of a new run, with the prompt it sends and its record."""
    folder = RUNS / str(number)
    folder.mkdir(parents=True)
    (folder / "prompt.txt").write_text(PROMPT.read_text())
    route = json.loads((ROOT / "model-route.json").read_text())
    record = {"fingerprint": code, "model": route.get("model"), "route": route.get("route"),
              "date": datetime.date.today().isoformat(), "replies": "From the model, through model.py."}
    (folder / "run.json").write_text(json.dumps(record, indent=2) + "\n")


def send(folder, notes, total):
    """Run the extractor on each note, one model call for each note, and keep each reply as it came."""
    sys.path.insert(0, str(ROOT))
    from extractor import ExtractionFailed, extract
    from model import ask

    def one(note):
        kept = []

        def recording(system_prompt, note_text, schema=None):
            kept.append(ask(system_prompt, note_text, schema))
            return kept[-1]

        try:
            extract((ROOT / "notes" / f"{note}.txt").read_text(), ask=recording)
        except ExtractionFailed:
            pass  # The reply stays as it came. The score counts it as a failure.
        (folder / f"{note}.txt").write_text(kept[-1])

    print(f"{total - len(notes)} of the {total} notes have a reply for this prompt. "
          f"The extractor sends the other {len(notes)} to the model, one call for each note.", flush=True)
    stopped = None
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    futures = [pool.submit(one, note) for note in notes]
    saved = 0
    print("Replies saved:", end="", flush=True)
    for future in concurrent.futures.as_completed(futures):
        if future.cancelled():
            continue
        if future.exception() is not None:  # The route to the model failed: stop, and keep what came back.
            stopped = stopped or future.exception()
            for waiting in futures:
                waiting.cancel()
            continue
        saved += 1
        print(f" {saved}", end="", flush=True)
    pool.shutdown(wait=True)
    print(flush=True)  # ends the line of replies saved
    if stopped:
        sys.exit(f"Stopped: {stopped}\nThe replies saved so far stay in {folder.relative_to(ROOT)}. "
                 "Run python3 ~/practice/check_setup.py to check the route to the model. Then run this again.")


def main():
    args = sys.argv[1:]
    if args not in ([], ["--first"]):
        sys.exit("Usage: python3 evaluation/score.py, or python3 evaluation/score.py --first")
    labels = load_labels()
    schema_text = SCHEMA.read_text()
    schema = json.loads(schema_text)
    known = runs()
    if args == ["--first"]:
        if 1 not in known:
            sys.exit("There is no first run in evaluation/runs/1. Run python3 ~/practice/reset.py score-the-prompt.")
        number = 1
    else:
        if not PROMPT.is_file():
            sys.exit("There is no prompts/system.txt. Put it back as the tag first-score has it: "
                     "git checkout first-score -- prompts/system.txt")
        prompt_text = PROMPT.read_text()
        first = RUNS / "1" / "prompt.txt"
        if first.is_file() and same_words(prompt_text, first.read_text()):
            print("prompts/system.txt is still the teammate's prompt, the prompt of the set's first run. "
                  "Change it. Then run this again.")
            return
        code = fingerprint(prompt_text, schema_text)
        number = next((n for n, (_, record) in known.items() if record.get("fingerprint") == code), None)
        if number is None:
            number = max(known, default=0) + 1
            new_run(number, code)
            known = runs()
        folder = known[number][0]
        missing = [note for note in sorted(labels) if note not in replies_in(folder)]
        if missing:
            send(folder, missing, len(labels))
        else:
            print(f"Each of the {len(labels)} notes has a reply for this prompt, so no note goes to the model.")
    folder = known[number][0]
    counts, wrong, failed = score(labels, replies_in(folder), schema)
    text = report(number, labels, counts, wrong, failed)
    (folder / "score.txt").write_text(text)
    lines = text.splitlines()
    print(lines[0])  # the run, and the replies that fail the schema
    if args == ["--first"]:
        print("\n".join(lines[3:4 + len(FIELDS)]))  # the precision and the recall of each field
    print(f"Each wrong value is in evaluation/runs/{number}/score.txt.")
    if len(known) > 1 and args != ["--first"]:
        print("Each run of the set, with the precision and the recall of each field:")
        for n, (other, _) in known.items():
            mark = " (this prompt)" if n == number else ""
            print(f"  the set's run {n}: {summary(score(labels, replies_in(other), schema)[0])}{mark}")


if __name__ == "__main__":
    main()
