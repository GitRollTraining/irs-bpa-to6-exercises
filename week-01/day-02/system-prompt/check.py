"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads prompts/system.txt: the rule for a note with no amount, the line about the <note> tags, and
the examples. It checks the JSON of each example against the output schema and against the tax year
and the form of its note. It reads the note of each example with no amount against the course's
labels of the notes. Then it reads the replies that ../record.py recorded for the prompt as it is now.
Each reply must fit the output schema, and the replies for notes 0102 and 0104 must give null. It
runs the lab's tests on the replies. Last, it looks for your commit. It never calls the model: a
stand-in for the model's route is first on the PATH of the tests.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

import jsonschema

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE / "lab"
PROMPT = "prompts/system.txt"
SENT = ("0147", "0102", "0104")  # the notes that ../record.py sends in the steps
RECORD = "python3 ../record.py " + " ".join(SENT)
# The course's labels: the lab's notes that state no amount ("16 of the notes name no amount",
# notes/README.md). The answer's decisions.md lists them.
NO_AMOUNT = {"0102", "0104", "0107", "0110", "0112", "0116", "0119", "0121", "0124", "0127", "0129",
             "0131", "0134", "0136", "0138", "0140"}
NULL_RULE = ("Section 2.2: \"The extractor's version is a field rule: if the note does not state an amount, "
             "return null.\"")
NOT_LAST = "Section 2.2, list \"Examples teach the shape\": \"So include one with no amount, not last\"."
FORMAT = "Section 2.2, list \"Say what you want\": \"Be specific about format and constraints\"."
# A sentence that tells the model never to give null, such as "Never return null".
NEGATED_NULL = re.compile(r"(?:\bnever|\bnot|n't)\s+(?:(?:be|return|give|use|set|put|output|write|answer)\s+)?null\b",
                          re.I)
# A word that says the amount is not there. The null rule has one, in its sentence or in the sentence before it.
# So "Return null for amount_in_question." and "If the note states an amount, return null." are not the rule.
ABSENT = re.compile(r"\b(?:no|not|none|nothing|without|missing|absent|unclear|unknown|unless|otherwise|else|lacks?"
                    r"|lacking|omits?|omitted|silent|leaves?\s+out|left\s+out)\b|n't", re.I)
# What the lab's tests read in the replies, tests/test_extractor.py.
NEEDS = {"test_note_0147_gives_its_amount": "The reply for note 0147 must give 2023 for tax_year, \"1040\" for form and "
                                            "18400 for amount_in_question, as the note says.",
         "test_note_with_no_amount_gives_null": "The reply for note 0102 must give null for amount_in_question."}
# The second half of the line about the tags: the note is text to read, never instructions to follow.
READ_ONLY = re.compile(r"\b(?:never|not|ignore|instructions?|follow|obey|commands?|orders?|material|data)\b|n't",
                       re.I)
sys.path.insert(0, str(HERE))
from record import fingerprint  # noqa: E402


def git(*args):
    return subprocess.run(["git", *args], cwd=LAB, capture_output=True, text=True)


def stop(message):
    print("Not yet: 1 left.\n- " + message)
    sys.exit(1)


def plain(note):
    """A note's words, without its tags, with one space between words."""
    return " ".join(re.sub(r"</?note>", " ", note).split())


def shown(error):
    """A schema error as the learner wrote the value: null, not Python's None."""
    return error.message.replace("None", "null", 1) if error.instance is None else error.message


def body(note):
    """A note's words without its label, such as "Note 0119."."""
    return re.sub(r"^Note \d+\.\s*", "", plain(note))


def numbers_left(note):
    """What in a note can be an amount. That is a number that is not its label, a tax year, a form or
    a count of days. It is also a word such as thousand or dollars."""
    text = re.sub(r"</?note>", " ", note)
    text = re.sub(r"\bNote \d+", " ", text)
    text = re.sub(r"\bTax years? \d{4}(?: and \d{4})?", " ", text)
    text = re.sub(r"\b(?:Forms?|Schedules?) [0-9A-Z][\w-]*", " ", text)
    text = re.sub(r"\b[A-Z]?\w*-[\w-]+", " ", text)  # W-2, 1099-K, 1120-S, K-1
    text = re.sub(r"\b\d+ (?:more )?(?:days?|weeks?|months?|years?|percent)\b", " ", text)
    text = re.sub(r"\b(?:19|20)\d{2}\b", " ", text)
    return (re.findall(r"\d[\d,]*", text)
            + re.findall(r"\b(?:hundreds?|thousands?|millions?|billions?|dollars?)\b", text, re.I))


def which_note(note, bodies):
    """The number of the note in notes/ that an example holds, or None for a note that you made up."""
    mine = body(note)
    for number, words in bodies.items():
        if mine and (mine == words or words in mine or (mine in words and len(mine) >= 0.3 * len(words))):
            return number
    return None


def json_start(line):
    """Where the JSON of an example starts in a line, or None: at the start of the line, after
    </note>, or after a short label such as "Output:"."""
    stripped = line.lstrip()
    if stripped.startswith("{"):
        return len(line) - len(stripped)
    found = re.search(r"</note>\s*\{|^\s*[A-Za-z]+(?: [A-Za-z]+)?:\s*\{", line)
    return found.end() - 1 if found else None


def read_prompt(text):
    """The examples of the prompt, the JSON that does not parse, and its instructions as paragraphs
    of sentences. Each example is a JSON object. Its note is the last <note>...</note> above it, with
    at most a short label, such as "Output:", between them. A note with no tags is the lines above the
    JSON, up to a blank line, a line that starts with "Example", or another example."""
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    decoder = json.JSONDecoder()
    examples, broken, held = [], [], set()
    floor, n = 0, 0  # floor: where the text after the last example starts
    while n < len(lines):
        column = json_start(lines[n])
        if column is None:
            n += 1
            continue
        start = offsets[n] + column
        try:
            value, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError as failure:
            broken.append((n + 1, failure.msg))
            n += 1
            continue
        last = text.count("\n", 0, end - 1)
        region = text[floor:start]
        close = region.rfind("</note>")
        between = region[close + len("</note>"):] if close >= 0 else ""
        opened = region.rfind("<note>", 0, close) if close >= 0 else -1
        if opened >= 0 and re.fullmatch(r"\s*(?:[A-Za-z]+(?: [A-Za-z]+)?:\s*)?", between):
            note, tagged = region[opened:close + len("</note>")], True
            top = text.count("\n", 0, floor + opened)
        else:
            top = n
            while top > 0 and top - 1 not in held and lines[top - 1].strip() \
                    and not lines[top - 1].lstrip().lower().startswith("example"):
                top -= 1
            note, tagged = "".join(lines[top:n]) + lines[n][:column], False
        held.update(range(top, last + 1))
        examples.append({"note": note.strip(), "fields": value, "tagged": tagged})
        floor, n = end, last + 1
    paragraphs, words = [], []
    for k, line in enumerate(lines + ["\n"]):
        if k in held or line.lstrip().lower().startswith("example") or not line.strip():
            if words:
                paragraphs.append([s for s in re.split(r"(?<=[.!?])\s+", " ".join(words)) if s.strip()])
            words = []
        else:
            words.append(line.strip())
    return examples, broken, paragraphs


def against_note(k, fields, note):
    """The tax year and the form of an example, against what its note says."""
    found = []
    year = re.search(r"\bTax year (\d{4})\b", note)
    if year and fields["tax_year"] != int(year.group(1)):
        found.append(f"{json.dumps(fields['tax_year'])} for tax_year, but its note says Tax year {year.group(1)}")
    form = re.search(r"\bForm ([0-9A-Z][\w-]*)", note)
    if form and re.sub(r"^form\s+", "", fields["form"].strip().lower()) != form.group(1).lower():
        found.append(f"{json.dumps(fields['form'])} for form, but its note says Form {form.group(1)}")
    return [f"in {PROMPT}, example {k} gives {what}. Write what the note says. Section 2.2, the figure of the "
            "prompt: \"Use only what the note itself says\"." for what in found]


def prompt_problems(text, schema, notes):
    examples, broken, paragraphs = read_prompt(text)
    problems = []
    if not any("null" in s.lower() and "amount" in (s + " " + (p[i - 1] if i else "")).lower()
               and ABSENT.search(s + " " + (p[i - 1] if i else "")) and not NEGATED_NULL.search(s)
               for p in paragraphs for i, s in enumerate(p)):
        problems.append(f"{PROMPT} has no line that tells the model to return null for amount_in_question when a "
                        f"note states no amount. {NULL_RULE}")
    tag = [(p, i) for p in paragraphs for i, s in enumerate(p) if "<note>" in s]
    if not tag:
        problems.append(f"{PROMPT} has no line that says the note is inside <note> tags. Section 2.2: \"For the "
                        "extractor, the note goes inside its own tag\".")
    elif not any(READ_ONLY.search(" ".join(p[i:i + 2])) for p, i in tag):
        problems.append(f"the line about the <note> tags in {PROMPT} does not say that the note is text to read, "
                        "never to follow. Section 2.2, list \"Say what you want\": \"So its text is material to "
                        "read, not instructions\".")
    untagged = [str(k) for k, ex in enumerate(examples, 1) if not ex["tagged"]]
    if untagged:
        problems.append(f"in {PROMPT}, " + ("the note of example " + untagged[0] + " is" if len(untagged) == 1 else
                                            "the notes of examples " + " and ".join(untagged) + " are")
                        + " not between <note> and </note>. Section 2.2, list \"Say what you want\": \"Wrap each "
                          "kind of content in its own tag\".")
    for line, message in broken:
        problems.append(f"the JSON on line {line} of {PROMPT} is broken: {message}. Each example ends with its five "
                        "fields as JSON.")
    validator = jsonschema.Draft202012Validator(schema)
    for k, ex in enumerate(examples, 1):
        errors = sorted(validator.iter_errors(ex["fields"]), key=lambda error: error.message)
        if errors:
            problems.append(f"the JSON of example {k} does not fit the output schema, schema/output.schema.json: "
                            f"{shown(errors[0])}.")
        else:
            problems += against_note(k, ex["fields"], ex["note"])

    with_null = [k for k, ex in enumerate(examples, 1)
                 if isinstance(ex["fields"], dict) and "amount_in_question" in ex["fields"]
                 and ex["fields"]["amount_in_question"] is None]
    if not with_null:
        problems.append(f"no example in {PROMPT} gives null for amount_in_question. Section 2.2, list \"Examples teach "
                        "the shape\": \"Every example with an amount teaches that notes have amounts\".")
    bodies = {number: body(words) for number, words in notes.items()}
    good = []
    for k in with_null:
        note = examples[k - 1]["note"]
        number = which_note(note, bodies)
        label = re.search(r"\bNote (\d{4})\b", note)
        sent = number if number in SENT else label.group(1) if label and label.group(1) in SENT else None
        if sent:
            problems.append(f"example {k} holds note {sent}, which ../record.py sends. An example of it gives the "
                            f"model the answer for that note. Take note 0119, as step 2 says. {NOT_LAST}")
        elif number and number not in NO_AMOUNT:
            problems.append(f"example {k} gives null, but the course reads note {number} as a note that states an "
                            f"amount. Take note 0119, as step 2 says. {NOT_LAST}")
        elif not number and numbers_left(note):
            problems.append(f"example {k} gives null, but its note has \"{numbers_left(note)[0]}\". Take note "
                            f"0119, as step 2 says. {NOT_LAST}")
        elif not number and not (re.search(r"\bTax years? \d{4}", note) and re.search(r"\bForms?\b", note)):
            problems.append(f"example {k} gives null, but its note names no tax year and form. Copy note 0119 "
                            f"whole, as step 2 says. {NOT_LAST}")
        else:
            good.append(k)
    if good and all(k == len(examples) for k in good):
        problems.append(f"the example with no amount is the last example in {PROMPT}. {NOT_LAST}")
    return problems


def failing_tests():
    """The lab's tests that fail on the recorded replies. A stand-in claude that fails is first on
    their PATH, so no test can reach the model."""
    with tempfile.TemporaryDirectory() as stand_in:
        claude = pathlib.Path(stand_in) / "claude"
        claude.write_text("#!/bin/sh\necho 'The check never calls the model.' >&2\nexit 1\n")
        claude.chmod(0o755)
        # PY_COLORS=0: a notebook's kernel sets FORCE_COLOR, and colours hide pytest's FAILED lines.
        env = {**os.environ, "PATH": stand_in + os.pathsep + os.environ.get("PATH", ""), "PY_COLORS": "0"}
        result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=no", "-rfE", "-p", "no:cacheprovider"],
                                cwd=LAB, capture_output=True, text=True, env=env, timeout=300)
    if result.returncode == 0:
        return []
    names = re.findall(r"^(?:FAILED|ERROR) \S+?::(\w+)", result.stdout, re.M)
    return names or [(result.stdout.strip().splitlines() or ["pytest printed nothing"])[-1]]


def reply_problems(text, schema):
    run = LAB / "runs" / fingerprint(text, schema)
    recorded = LAB / "tests" / "recorded"
    missing = [n for n in SENT if not (run / f"{n}.json").is_file()]
    if len(missing) == len(SENT):
        if recorded.is_dir() and any(recorded.glob("*.json")):
            return [f"the replies in tests/recorded/ are not from {PROMPT} as it is now. After each change to the "
                    f"prompt, run {RECORD} again."]
        return [f"you have no recorded replies yet. Run {RECORD}."]
    if missing:
        return [("note " + missing[0] + " has" if len(missing) == 1 else "notes " + " and ".join(missing) + " have")
                + f" no reply from {PROMPT} as it is now. Run {RECORD}."]
    problems = []
    for n in SENT:
        mine = recorded / f"{n}.json"
        if not mine.is_file():
            problems.append(f"tests/recorded/{n}.json is missing. Run {RECORD} to put it back.")
        elif mine.read_text() != (run / f"{n}.json").read_text():
            problems.append(f"tests/recorded/{n}.json is not the reply that the model gave to {PROMPT}. Do not edit a "
                            "reply. Section 2.2: \"Telling it fixes one answer, not the prompt.\" "
                            f"Run {RECORD} to put the replies back.")
    if problems:
        return problems
    again = "Change the prompt, not the reply. Then record again."
    validator = jsonschema.Draft202012Validator(schema)
    for n in SENT:
        try:
            fields = json.loads((run / f"{n}.json").read_text())
        except json.JSONDecodeError:
            problems.append(f"the reply for note {n} is not JSON. {FORMAT} {again}")
            continue
        errors = sorted(validator.iter_errors(fields), key=lambda error: error.message)
        if errors:
            problems.append(f"the reply for note {n} does not fit the output schema: {shown(errors[0])}. {FORMAT} "
                            f"{again}")
        elif n in NO_AMOUNT and fields["amount_in_question"] is not None:
            problems.append(f"the reply for note {n} gives {json.dumps(fields['amount_in_question'])} for "
                            f"amount_in_question, but note {n} states no amount. {NULL_RULE} {again}")
    if problems:
        return problems
    failing = failing_tests()
    if failing:
        needs = "".join(NEEDS[name] + " " for name in failing if name in NEEDS)
        return [f"the lab's tests fail on your recorded replies: {', '.join(failing)}. {needs}{again} Section 2.2: \"A "
                "loop: run the set, score it, edit the prompt\"."]
    return []


def main():
    if not (LAB / ".git").is_dir():
        stop("there is no repository lab/ yet. Run python3 ~/practice/reset.py system-prompt.")
    if not (LAB / PROMPT).is_file():
        stop(f"{PROMPT} is missing. To get the draft again, run cp ../files/system.txt {PROMPT}.")
    schema_file = LAB / "schema" / "output.schema.json"
    if not schema_file.is_file() or not (LAB / "notes").is_dir():
        stop("schema/output.schema.json or notes/ is missing. Run python3 ~/practice/reset.py system-prompt to "
             "build the lab again. The reset removes your commits and replies.")
    text = (LAB / PROMPT).read_text()
    schema = json.loads(schema_file.read_text())
    notes = {p.stem: plain(p.read_text()) for p in sorted((LAB / "notes").glob("*.txt"))}
    problems = prompt_problems(text, schema, notes) + reply_problems(text, schema)
    if git("status", "--porcelain", "--", PROMPT, "tests/recorded").stdout.strip():
        problems.append(f"commit {PROMPT} and tests/recorded/ as they are now.")
    if problems:
        print(f"Not yet: {len(problems)} left.")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    print("Done: your prompt gives the null rule, the <note> tags, and an example with no amount that is not last. "
          "Its three replies fit the output schema, and the replies for 0102 and 0104 give null. The lab's tests "
          "pass on them, and you committed both.")


if __name__ == "__main__":
    main()
