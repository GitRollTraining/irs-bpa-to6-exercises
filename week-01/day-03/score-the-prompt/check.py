"""The done check for this exercise. From extractor/, run: python3 ../check.py

It reads your write-up evaluation/failure.md, the prompt, and the runs in evaluation/runs/. It scores
the saved replies itself, with the scorer, the labels and the first run as supplied. It calls no
model. It looks for these:

- a note and a field that the first run got wrong, and the lines of the teammate's prompt that led to it
- a changed prompt, with a reply for each labelled note, that gets more of that field right than the first run
- the notes, the labels, the scorer, the schema, the extractor and the first run, as supplied
- your commit
"""
import json
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE / "extractor"
TAG = "first-score"
sys.path.insert(0, str(HERE / "files" / "evaluation"))
import score as scorer  # noqa: E402  (the scorer as supplied. The check never calls its send function.)

PAGE = "evaluation/failure.md"
PROMPT = "prompts/system.txt"
SCHEMA = "schema/output.schema.json"
FIRST = "evaluation/runs/1"
FIRST_SCORE = f"{FIRST}/score.txt"
TEAMMATE_PROMPT = f"{FIRST}/prompt.txt"  # the teammate's prompt, as the first run sent it
KEPT = ["notes", "evaluation/labels.jsonl", "evaluation/score.py", FIRST, SCHEMA, "extractor.py", "model.py",
        "model-route.json"]
FIELD_NAMES = {"tax_year": r"\btax[ _]year\b", "form": r"\bform\b",
               "amount_in_question": r"\bamount(?:[ _]in[ _]question)?\b"}
# The notebook lines that the messages quote. The Why column of the table in step 2 quotes RULE_FIELD for Note: and
# Field:, RULE_SHAPE for Cause: and RULE_LOOP for the change. RULE_COMPARE, RULE_FIXED and RULE_COMMIT rule on the
# score of your prompt, the files that stay as supplied, and the commit. RULE_SAY rules on a line about the form, for
# a run that still gets form wrong after the change. RULE_LOOK rules on the score that goes to the trainer, for a run
# that still gets form wrong with both changes in the prompt.
LOOP_PLACE = 'Day 2, section 2.2, under "Revise by editing the prompt, then re-score the whole set."'
RULE_FIELD = ('Section 3.3, the list "Score the fields, not the note": "Per field, the score names the instruction '
              'to change".')
RULE_SHAPE = ('Day 2, section 2.2, the list "Examples teach the shape": "Every example with an amount teaches that '
              'notes have amounts".')
RULE_LOOP = f'{LOOP_PLACE}: "A loop: run the set, score it, edit the prompt".'
RULE_COMPARE = f'{LOOP_PLACE}: "Then run the whole set again, and compare".'
RULE_FIXED = ('Section 3.3, the list "The evaluation set": "A fixed set of labelled cases, scored the same way every '
              'time".')
RULE_COMMIT = 'Day 1, "Opening", the list "How we work": "Each step ends in a commit: a place to stop".'
RULE_SAY = 'Day 2, section 2.2, the list "Say what you want": "Be specific about format and constraints".'
RULE_LOOK = ('Section 3.3, under "Start by looking, not by measuring.": "Each note beside its JSON and the JSON it '
             'should be".')
CHANGE = (f'In lines 11 and 17 of {PROMPT}, write "form": "1040" in place of "form": "Form 1040", as the table in '
          'step 2 says.')
SCORE_IT = "Score it on the whole set, as step 2 says: run python3 evaluation/score.py, or cell 2 in the notebook."


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def supplied(path):
    """A file as the start supplied it, from the commit with the tag first-score."""
    shown = git("show", f"{TAG}:{path}")
    return shown.stdout if shown.returncode == 0 else None


def stop(message):
    print("Not yet: 1 left.")
    print("- " + message)
    sys.exit(1)


def parts(text):
    """The answers at the bottom of the write-up, by their labels Note, Field and Cause.
    An answer goes on to the next label, so a cause can take more than one line."""
    found, label = {}, None
    for line in text.splitlines():
        start = re.match(r"(Note|Field|Cause):(.*)$", line)
        if start:
            label = start.group(1)
            found[label] = start.group(2).strip()
        elif label:
            found[label] = (found[label] + "\n" + line).strip()
    return found


def cause_lines(text, count):
    """The line numbers that a cause names, from 1 to count: each number, and each range such as 8 to 17 or 8-17.
    A larger number, such as the 1040 of a form, is not a line."""
    span = r"\b(\d+)\s*(?:-|–|to)\s*(\d+)\b"
    found = {line for first, last in re.findall(span, text) for line in range(int(first), int(last) + 1)}
    found.update(int(number) for number in re.findall(r"\b\d+\b", re.sub(span, " ", text)))
    return {line for line in found if 1 <= line <= count}


def examples(prompt_lines, field):
    """The numbers of the lines of a prompt that give the field a value in an example reply."""
    return {number for number, line in enumerate(prompt_lines, 1) if f'"{field}":' in line}


def has_change(prompt_text):
    """True when each example reply of the prompt gives "form": "1040", as the table in step 2 says. In the teammate's
    prompt, these are lines 11 and 17. A new line above them moves them down."""
    lines = prompt_text.splitlines()
    shown = examples(lines, "form")
    return len(shown) >= 2 and all(re.search(r'"form":\s*"1040"', lines[number - 1]) for number in shown)


def next_move(field, run):
    """What to do when your run gets the field no more right than the first run. First comes the change of the table
    in step 2, then a line about the form. With both in your prompt, the check has no other change to give."""
    prompt_now = (REPO / PROMPT).read_text()
    if field != "form" or not has_change(prompt_now):
        return f"{CHANGE} {SCORE_IT} {RULE_LOOP}"
    if not re.search(r"form number only", prompt_now, re.I):
        return (f"Your prompt has the change, but the replies of your run still get form wrong. Below line 4 of "
                f"{PROMPT}, add this line: \"Give form as the form number only.\" For a new prompt, score.py sends "
                f"the 20 notes again. {SCORE_IT} {RULE_SAY}")
    return ("Your prompt has both changes: the examples of step 2, and a line that asks for the form number only. "
            "But the replies of your run still get form wrong. So the check has no other change to give. Show "
            f"{run.relative_to(REPO).as_posix()}/score.txt to your trainer. It names each note that your run got "
            f"wrong. {RULE_LOOK}")


def pair(counts, field):
    """The precision and the recall of one field, as the scorer prints them."""
    c = counts[field]
    return f"{scorer.ratio(c['correct'], c['extracted'])}/{scorer.ratio(c['correct'], c['expected'])}"


def page_problems(text, wrong, labels):
    """What the write-up still needs: one wrong value of the first run, and its cause."""
    problems = []
    answers = parts(text)
    where = f"In {FIRST_SCORE}, each wrong value is in {' and '.join(sorted({field for _, field in wrong}))}."
    note_line, field_line = answers.get("Note"), answers.get("Field")
    notes = [note.zfill(4) for note in re.findall(r"\b\d{1,4}\b", note_line or "")]  # 147 is note 0147
    fields = [field for field, pattern in FIELD_NAMES.items() if re.search(pattern, (field_line or "").lower())]
    if note_line is None or field_line is None:
        problems.append(f"{PAGE} no longer has its lines Note: and Field:. Write them again at the bottom of your "
                        f"write-up, as the table in step 2 says. {RULE_FIELD}")
    elif not notes or not field_line:
        problems.append(f"{PAGE}: Note: and Field: do not name a wrong value yet. Write Note: 0147 and Field: form, "
                        f"as the table in step 2 says. {where} {RULE_FIELD}")
    elif len(fields) != 1:
        problems.append(f"{PAGE}: after Field:, write one field that the scorer compares: tax_year, form or "
                        f"amount_in_question. The table in step 2 gives form. {RULE_FIELD}")
    elif not any(note in labels for note in notes):
        problems.append(f"{PAGE}: note {notes[0]} is not one of the {len(labels)} labelled notes. Take a note from "
                        f"the wrong values in {FIRST_SCORE}, such as 0147, as the table in step 2 says. {RULE_FIELD}")
    elif not any((note, fields[0]) in wrong for note in notes):
        named = ", ".join(note for note in notes if note in labels)
        problems.append(f"{PAGE}: the first score has no wrong value in {fields[0]} for note {named}. {where} The "
                        f"table in step 2 gives Field: form. {RULE_FIELD}")
    # The cause: the lines of the teammate's prompt whose example replies give the field its value, or missing for
    # the line that tells the model how to write it.
    cause = answers.get("Cause")
    teammate = (supplied(TEAMMATE_PROMPT) or "").splitlines()
    field = fields[0] if len(fields) == 1 else "form"
    named, lacks = cause_lines(cause or "", len(teammate)), re.search(r"\bmissing\b", (cause or "").lower())
    if cause is None:
        problems.append(f"{PAGE} no longer has its line Cause:. Write it again at the bottom of your write-up, as "
                        f"the table in step 2 says. {RULE_SHAPE}")
    elif not named and not lacks:
        problems.append(f"{PAGE}: Cause: names no line of the teammate's prompt. Write the numbers of the lines that "
                        f"led to that value. The table in step 2 gives Cause: 11, 17. {RULE_SHAPE}")
    elif not lacks and not named & examples(teammate, field):
        problems.append(f"{PAGE}: no line that Cause: names gives {field} its value in the teammate's prompt. Its "
                        'lines 11 and 17 are the replies of the two examples, which write "Form 1040". The table in '
                        f"step 2 gives Cause: 11, 17. {RULE_SHAPE}")
    return problems


def your_run(labels):
    """The folder of the run of the prompt as it is now, or a problem when that run is not complete."""
    if not (REPO / PROMPT).is_file():
        return None, (f"{PROMPT} is missing. Put it back as the tag {TAG} has it: git checkout {TAG} -- {PROMPT}. "
                      f"Then make the change of the table in step 2. {RULE_LOOP}")
    prompt_now = (REPO / PROMPT).read_text()
    if scorer.same_words(prompt_now, supplied(PROMPT) or ""):
        return None, f"{PROMPT} is still the teammate's prompt. {CHANGE} {SCORE_IT} {RULE_LOOP}"
    schema_now = (REPO / SCHEMA).read_text() if (REPO / SCHEMA).is_file() else ""
    code = scorer.fingerprint(prompt_now, schema_now)
    run = next((folder for folder, record in scorer.runs(REPO / "evaluation" / "runs").values()
                if record.get("fingerprint") == code), None)
    missing = sorted(set(labels) - set(scorer.replies_in(run))) if run else sorted(labels)
    if missing:
        return None, (f"your {PROMPT} has no reply yet for {len(missing)} of the {len(labels)} labelled notes. "
                      f"{SCORE_IT} {RULE_COMPARE}")
    return run, None


def main():
    if not (REPO / ".git").is_dir() or git("rev-parse", "-q", "--verify", f"refs/tags/{TAG}").returncode:
        stop(f"there is no repository extractor/ with the tag {TAG}. Run python3 ~/practice/reset.py score-the-prompt.")
    labels = scorer.load_labels(HERE / "files" / "evaluation" / "labels.jsonl")
    schema = json.loads(supplied(SCHEMA))
    first = {note: supplied(f"{FIRST}/{note}.txt") for note in labels}
    first_counts, wrong_values, _ = scorer.score(labels, {n: r for n, r in first.items() if r is not None}, schema)
    wrong = {(note, field) for note, field, _, _ in wrong_values}

    run, run_problem = your_run(labels)
    yours = scorer.score(labels, scorer.replies_in(run), schema)[0] if run is not None else None

    page = REPO / PAGE
    if page.is_file():
        problems = page_problems(page.read_text(), wrong, labels)
    else:
        problems = [f"{PAGE} is missing. Put it back as the tag {TAG} has it: git checkout {TAG} -- {PAGE}. Then "
                    f"write the answers of the table in step 2. {RULE_FIELD}"]
    if run_problem:
        problems.append(run_problem)
    else:
        # Done means it works: your run gets more of each failed field right than the first run.
        for field in sorted({field for _, field in wrong}):
            if yours[field]["correct"] <= first_counts[field]["correct"]:
                problems.append(f"in the score of your prompt, {field} is {pair(yours, field)}, no better than the "
                                f"{pair(first_counts, field)} of the first score. So the change did not fix the "
                                f"failure. {next_move(field, run)}")

    changed = [path for path in KEPT if git("diff", "--quiet", TAG, "--", path).returncode != 0]
    for path in changed:
        what = {FIRST: "the first run, " + FIRST + ",", "notes": "a note in notes/"}.get(path, path)
        problems.append(f"{what} is not as supplied. This exercise changes only the prompt and the write-up, so "
                        f"that the two scores compare. Put it back: git checkout {TAG} -- {path}. {RULE_FIXED}")

    pending = []
    for entry in git("status", "--porcelain", "--", PROMPT, "evaluation").stdout.splitlines():
        path = entry[3:].strip('"')
        folder = re.match(r"evaluation/runs/[^/]+/", path)
        path = folder.group(0) if folder else path
        # A file that is not as supplied has its own line above, which puts it back. It is not one to commit.
        if path not in pending and not any(path == kept or path.startswith(f"{kept}/") for kept in changed):
            pending.append(path)
    if pending:
        problems.append("commit your changes, as step 3 says. In the notebook, set commit = True in cell 3. Then run "
                        f"cell 3. In a terminal, run git add {PROMPT} evaluation. Then run git commit -m \"Revise the "
                        "prompt once\". Not committed: " + ", ".join(pending) + f". {RULE_COMMIT}")

    if problems:
        print(f"Not yet: {len(problems)} left.")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    both = ", ".join(f"{field} {pair(first_counts, field)} then {pair(yours, field)}" for field in scorer.FIELDS)
    print(f"Done: the set scored your prompt on the same notes and labels. Precision/recall, the teammate's prompt "
          f"then yours: {both}. You committed it.")


if __name__ == "__main__":
    main()
