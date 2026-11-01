"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads the schema in lab/schema/output.schema.json, with sample replies. It gives the eight
replies to check_reply in lab/extractor.py, and more replies that it makes from them. When it finds
nothing else, it runs the lab's tests. It reads lab/ as it is now, from its first run. It never
calls the model. A claude and a codex that stop at once come first on the PATH of your code
and of the tests.
"""
import atexit
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import traceback

import jsonschema

sys.dont_write_bytecode = True
# A claude and a codex that stop at once come first on PATH, so no code that the check runs can reach the model.
STAND_INS = pathlib.Path(tempfile.mkdtemp(prefix="validate-replies-check-"))
atexit.register(shutil.rmtree, STAND_INS, True)
for _name in ("claude", "codex"):
    (STAND_INS / _name).write_text("#!/bin/sh\necho 'The check never calls the model.' >&2\nexit 1\n")
    (STAND_INS / _name).chmod(0o755)
os.environ["PATH"] = str(STAND_INS) + os.pathsep + os.environ.get("PATH", "")

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE / "lab"
KIT = next(p for p in HERE.parents if (p / "notes").is_dir())
SCHEMA_FILE = "schema/output.schema.json"
CODE_FILE = "extractor.py"
FIELDS = ("tax_year", "form", "issue", "amount_in_question", "next_action")
# The course's copies of the eight replies, so that an edit in lab/replies/ changes nothing here.
REPLIES = {f"replies/{p.name}": p.read_text() for p in sorted((HERE / "files" / "replies").glob("*.txt"))}
GOOD = json.loads(REPLIES["replies/0147.txt"])  # a reply that passes. The replies made below start from it.
# The tax years that the course's notes name: "Tax year 2023", or "Tax years 2022 and 2023".
NOTE_YEARS = sorted({int(year) for note in (KIT / "notes").glob("*.txt")
                     for found in re.findall(r"Tax years? (\d{4})(?: and (\d{4}))?", note.read_text())
                     for year in found if year})
# Replies made from replies/0147.txt, each named as a message shows it.
MADE = {
    "replies/0147.txt with tax year 2203": {**GOOD, "tax_year": 2203},
    "replies/0147.txt with the amount as text": {**GOOD, "amount_in_question": "18,400"},
    "replies/0147.txt with no tax_year": {k: v for k, v in GOOD.items() if k != "tax_year"},
    "replies/0147.txt with tax_year as text": {**GOOD, "tax_year": "2023"},
    **{f"replies/0147.txt with tax year {year}": {**GOOD, "tax_year": year} for year in NOTE_YEARS},
}
TEXT_AMOUNTS = ("replies/0104.txt", "replies/0105.txt", "replies/0147.txt with the amount as text")
YEAR_2203 = ("replies/0130.txt", "replies/0147.txt with tax year 2203")
NOT_JSON = ("replies/0113.txt", "replies/0121.txt")
# Where each answer is: the table in step 2, in README.md and in the notebook's slot alike.
ROW_1 = "Change only line 10, as row 1 of the table in step 2 gives it."
# The rules, in the words of the notebook of day 3, section 3.1, with where each one is.
BELOW_TABLE = "Section 3.1, below the table of fields:"
BELOW_FIGURE = "Section 3.1, below the second figure:"
IN_LIST = "Section 3.1, in the list above the second figure:"
TYPES = "Each field keeps the type that the table of fields in section 3.1 gives."
ONLY_AMOUNT = '"Only amount_in_question may be null, because the lab\'s notes always state the other four fields."'
KEEP_REQUIRED = '"For a value that may be absent, keep the field required and allow null"'
CONTRACT = '"The extractor\'s contract is three things: required, a type that allows null, and no extra keys."'
VALIDATES = '"So the extractor validates every reply against the schema and against simple checks of its own"'
NEVER_REPAIRED = '"a reply that fails is counted as a failure, never repaired by guessing"'
OWN_CHECK = '"Tax year 2203 passes the schema, not your own check"'
MAY_FAIL = '"May fail the schema: a refusal, a cut-off, capitalization"'
RELY_ON = 'Section 3.1, the list "What it buys": "A reply your code can rely on".'


def stop(message):
    """The check stops here, with one thing left."""
    print("Not yet: 1 left.")
    print("- " + message)
    sys.exit(1)


def listed(names):
    names = list(names)
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def parsed(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def restore(name):
    return f"there is no {name} in lab. To restore it as the last commit has it, run `git restore {name}` from lab."


def lines_run(function, text):
    """The numbers of the lines of function that run when it gets text."""
    run = set()

    def trace(frame, event, arg):
        if frame.f_code is not function.__code__:
            return None
        if event == "line":
            run.add(frame.f_lineno)
        return trace

    sys.settrace(trace)
    try:
        function(text)
    except Exception:  # the verdicts in code_problems report what it raises
        pass
    finally:
        sys.settrace(None)
    return run


def read_schema():
    """The schema in lab/, as a validator. The check stops when Python cannot read it."""
    if not (REPO / SCHEMA_FILE).is_file():
        stop(restore(SCHEMA_FILE))
    try:
        schema = json.loads((REPO / SCHEMA_FILE).read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
    except (OSError, ValueError) as failure:
        stop(f"Python cannot read {SCHEMA_FILE} as JSON ({failure}). {ROW_1}")
    except jsonschema.exceptions.SchemaError as failure:
        stop(f"{SCHEMA_FILE} is not a valid schema ({failure.message}). {ROW_1}")
    return jsonschema.Draft202012Validator(schema)


def schema_problems(validator):
    """What the schema lets pass that section 3.1 rules out, and what it stops that section 3.1 allows."""
    passes = validator.is_valid
    problems = []
    if not passes(GOOD):
        problems.append(f"{SCHEMA_FILE} fails replies/0147.txt, a good reply. {TYPES} {ROW_1}")
    nullable = [field for field in FIELDS if field != "amount_in_question" and passes({**GOOD, field: None})]
    if nullable:
        example = (' Note 0138 ends "Wait for the call.", but reply 0138 passes with null. Make line 10 '
                   '`"next_action": {"type": "string"}`, as row 1 of the table in step 2 says.'
                   if "next_action" in nullable else f" {ROW_1}")
        problems.append(f"{SCHEMA_FILE} lets {listed(nullable)} be null.{example} {BELOW_TABLE} {ONLY_AMOUNT}")
    if not passes({**GOOD, "amount_in_question": None}):
        problems.append(f"{SCHEMA_FILE} does not let amount_in_question be null, so no reply for a note with no amount "
                        f"can pass. {ROW_1} {BELOW_TABLE} {KEEP_REQUIRED}")
    left_out = [field for field in FIELDS if passes({k: v for k, v in GOOD.items() if k != field})]
    if left_out:
        problems.append(f"{SCHEMA_FILE} lets a reply have no {listed(left_out)}. {ROW_1} {BELOW_TABLE} {CONTRACT}")
    if passes({**GOOD, "confidence": 0.9}):
        problems.append(f"{SCHEMA_FILE} lets a reply add a key of its own. {ROW_1} {BELOW_TABLE} {CONTRACT}")
    other_types = {"tax_year": "2023", "form": 1040, "issue": ["Schedule C"], "amount_in_question": "18,400",
                   "next_action": 30}
    typed = [field for field, value in other_types.items() if passes({**GOOD, field: value})]
    if typed:
        problems.append(f"{SCHEMA_FILE} lets {listed(typed)} have a value of a different type. {TYPES} {ROW_1}")
    return problems


def code_problems(validator):
    """What check_reply in lab/extractor.py does with each reply, against section 3.1."""
    if not (REPO / CODE_FILE).is_file():
        stop(restore(CODE_FILE))
    sys.path.insert(0, str(REPO))
    try:
        import extractor
    except Exception as failure:  # the check reports an edit that stops extractor.py loading
        # Python names a line of row 3, or a line below it, such as `return fields` after a blank line. Each of the
        # two lines of row 3 names the tax year, so the check reads the named line and the two lines above it.
        if isinstance(failure, SyntaxError):
            number = failure.lineno or 0
        else:  # an error that the lines raise as extractor.py loads, such as row 3 pasted outside check_reply
            mine = [frame for frame in traceback.extract_tb(failure.__traceback__)
                    if pathlib.Path(frame.filename) == REPO / CODE_FILE]
            number = mine[-1].lineno if mine else 0
        lines = (REPO / CODE_FILE).read_text(errors="replace").splitlines() if number else []
        if "tax" in " ".join(lines[max(number - 3, 0):number]):
            move = ("Copy the two lines of row 3 of the table in step 2 as they are, just above `return fields`, after "
                    f"the schema check. Indent `if` and `return fields` four spaces, and `raise` eight. {IN_LIST} "
                    f"{OWN_CHECK}")
        else:
            move = "Look again at the lines of rows 2 and 3 of the table in step 2."
        stop(f"{CODE_FILE} does not load. Python reports {type(failure).__name__}: {failure}. {move}")

    def verdict(text):
        try:
            return "passes", extractor.check_reply(text)
        except extractor.ExtractionFailed as failure:
            return "failure", str(failure)
        except Exception as failure:  # any other stop is a problem of its own, below
            # The last line of extractor.py that ran tells which row of the table the stop comes from.
            mine = [frame for frame in traceback.extract_tb(failure.__traceback__)
                    if pathlib.Path(frame.filename) == REPO / CODE_FILE]
            where = (mine[-1].lineno, mine[-1].line or "") if mine else (None, "")
            return "stops", (f"{type(failure).__name__}: {failure}", *where)

    texts = dict(REPLIES)
    texts.update({name: json.dumps(reply) for name, reply in MADE.items()})
    seen = {name: verdict(text) for name, text in texts.items()}
    passed = [name for name, (state, _) in seen.items() if state == "passes"]
    problems = []

    # A reply that passes with nothing returned: a paste of row 3 moved or replaced `return fields`.
    nothing = [name for name in passed if seen[name][1] is None]
    if nothing:
        problems.append(f"{CODE_FILE}: check_reply returns nothing for {listed(nothing[:2])}, so your code gets no "
                        "fields from a reply that passes. End check_reply with `return fields`, at four spaces, below "
                        f"the two lines of row 3 of the table in step 2. {RELY_ON}")
    # A reply with an amount as text that check_reply passes and changes: the guess of the six lines that row 2
    # removes. One that it passes as it came has skipped the schema check, and has its line below.
    text_amount = [name for name in TEXT_AMOUNTS if name in passed and name not in nothing
                   and seen[name][1] != parsed(texts[name])]
    if text_amount:
        problems.append(f"{CODE_FILE}: check_reply passes {listed(text_amount[:2])}, whose amount is text. A guess "
                        "can turn the text into a wrong number. Remove the six lines from `# The model sometimes`, "
                        f"as row 2 of the table in step 2 says. {BELOW_FIGURE} {NEVER_REPAIRED}")
    changed = [name for name in passed if name not in TEXT_AMOUNTS + tuple(nothing)
               and seen[name][1] != parsed(texts[name])]
    if changed:
        problems.append(f"{CODE_FILE}: for {listed(changed[:2])}, check_reply returns values that the reply does not "
                        "have. Return each reply that passes as it came. Row 2 of the table in step 2 removes the "
                        f"lines that change a value. {BELOW_FIGURE} {NEVER_REPAIRED}")
    year_2203 = [name for name in YEAR_2203 if name in passed]
    # The learner's own check: a line of extractor.py that starts with if and names tax_year.
    own = {number for number, line in enumerate((REPO / CODE_FILE).read_text().splitlines(), 1)
           if line.strip().startswith("if ") and "tax_year" in line}
    never_run = bool(year_2203 and own and not own & lines_run(extractor.check_reply, texts[year_2203[0]]))
    if year_2203:
        if never_run:
            problems.append(f"{CODE_FILE}: the lines of row 3 of the table in step 2 never run, so check_reply passes "
                            f"{year_2203[0]}, with tax year 2203. Put them just above `return fields`, with `if` "
                            f"indented as `return fields`. {IN_LIST} {OWN_CHECK}")
        else:
            as_they_are = ", as they are" if own else ""
            problems.append(f"{CODE_FILE}: check_reply passes {year_2203[0]}, with tax year 2203. The schema passes "
                            f"any integer, so only your own check can fail it. Add the lines of row 3 of the table in "
                            f"step 2{as_they_are}. {IN_LIST} {OWN_CHECK}")
    blocked = [year for year in NOTE_YEARS if seen[f"replies/0147.txt with tax year {year}"][0] == "failure"]
    if blocked:
        these = "that year" if len(blocked) == 1 else "these years"
        problems.append(f"{CODE_FILE}: check_reply fails tax year {listed(map(str, blocked))}, and the notes in "
                        f"notes/ name {these}. Fail only a year after this year, as row 3 of the table in step 2 says. "
                        f"{IN_LIST} {OWN_CHECK}")
    for name in ("replies/0102.txt", "replies/0147.txt"):
        # A good reply that the schema fails has its line above, and one that the range fails too.
        if seen[name][0] == "failure" and validator.is_valid(parsed(texts[name])) and GOOD["tax_year"] not in blocked:
            problems.append(f"{CODE_FILE}: check_reply counts {name} as a failure ({seen[name][1]}). But that "
                            "reply is good: each field has the type that the table of fields in section 3.1 gives. "
                            "Make only the changes of rows 2 and 3 of the table in step 2.")
    not_json = [name for name in NOT_JSON if name in passed]
    if not_json:
        they = "it is" if len(not_json) == 1 else "they are"
        problems.append(f"{CODE_FILE}: check_reply passes {listed(not_json)}, and {they} not JSON. Keep the first "
                        "lines of check_reply, which fail such a reply. Rows 2 and 3 of the table in step 2 change no "
                        f"line there. {IN_LIST} {MAY_FAIL}")
    # A text amount that returns nothing passed the schema after the guess of row 2: it skipped no check.
    skipped = [name for name in passed if name not in text_amount + changed and name not in NOT_JSON
               and not (name in nothing and name in TEXT_AMOUNTS)
               and parsed(texts[name]) is not None and not validator.is_valid(parsed(texts[name]))]
    if skipped:
        problems.append(f"{CODE_FILE}: check_reply passes {listed(skipped[:2])}, which the schema fails. Keep the "
                        "schema check, and put your own check after it, as row 3 of the table in step 2 says. "
                        f"{BELOW_FIGURE} {VALIDATES}")
    stopped = [name for name, (state, _) in seen.items() if state == "stops"]
    error, number, line = seen[stopped[0]][1] if stopped else ("", None, "")
    # The lines of row 3: the `if` names tax_year, and the `raise` is the line just below it.
    in_row_3 = "tax_year" in line or "datetime" in line or (number is not None and number - 1 in own)
    # A stop on the lines of row 3 where they never run for tax year 2203 has its line above.
    if stopped and not (never_run and in_row_3):
        if error.startswith("NameError") and "datetime" in error:
            fix = "Put `import datetime` above `import json`, as row 3 of the table in step 2 says."
        elif not in_row_3:
            fix = ("Look again at row 2 of the table in step 2: remove the six lines from `# The model sometimes`, "
                   f"and no other line. {BELOW_FIGURE} {NEVER_REPAIRED}")
        elif set(stopped) <= {"replies/0147.txt with no tax_year", "replies/0147.txt with tax_year as text"}:
            fix = ("Put the two lines of row 3 of the table in step 2 just above `return fields`, after the schema "
                   "check. Before it, `tax_year` can be missing or text, and `>` stops with an error. In the second "
                   "figure of section 3.1, your own check comes after the schema.")
        else:
            fix = ("Copy the two lines of row 3 of the table in step 2 as they are, just above `return fields`. "
                   f"{IN_LIST} {OWN_CHECK}")
        at = f" at line {number}" if number else ""
        problems.append(f"{CODE_FILE}: check_reply stops with {error}{at}, for {stopped[0]}. {fix}")
    return problems


def tests_problems():
    # PY_COLORS=0: a notebook's kernel sets FORCE_COLOR, and colours change the lines that pytest prints.
    # COLUMNS=500: pytest cuts each FAILED line to the width of the terminal, and the reason is at its end.
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=no", "-rfE", "-p", "no:cacheprovider"],
                         cwd=REPO, capture_output=True, text=True, timeout=300,
                         env={**os.environ, "PY_COLORS": "0", "PYTHONDONTWRITEBYTECODE": "1", "COLUMNS": "500"})
    if run.returncode == 0:
        return []
    failed = [line for line in run.stdout.splitlines() if line.startswith(("FAILED ", "ERROR "))]
    first = failed[0] if failed else (run.stdout.strip().splitlines() or ["pytest printed nothing"])[-1]
    more = f" pytest names {len(failed) - 1} more." if len(failed) > 1 else ""
    return [f"some of the lab's tests fail. pytest reports `{first[:300]}`.{more} Make only the changes of the table "
            "in step 2."]


def main():
    if not (REPO / ".git").is_dir():
        stop("there is no repository lab/ yet. Run `python3 ~/practice/reset.py validate-replies`.")
    validator = read_schema()
    # The tests run only when the check finds nothing else: a fault that a line above names fails them too.
    problems = schema_problems(validator) + code_problems(validator) or tests_problems()
    if problems:
        print(f"Not yet: {len(problems)} left.")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    print("Done: only the amount may be null, and check_reply changes no reply and fails tax year 2203. "
          "The lab's tests pass.")


if __name__ == "__main__":
    main()
