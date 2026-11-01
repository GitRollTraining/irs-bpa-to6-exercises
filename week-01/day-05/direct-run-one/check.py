"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads what run 1 of your coding agent left in lab/, through Git. It runs the done-when of run 1
itself: python3 -m pytest tests/test_schema.py. Then it runs the same tests on a copy of lab/, two
times. Each time, it makes one change to the schema of the run in schema/. The first change takes
amount_in_question out of the required fields. The second change does not let amount_in_question be
null. A test that passes on the run, and fails or is not there after a change, holds that part of
the done-when. After each change, the check runs the tests one more time, with a change that keeps
what the schema accepts. A test that fails then reads the form of the schema and no output, so it
holds no part. The check compares these runs with your report, run-1-record.md. Then it reads your
commit. It never asks you to commit a run that fails its done-when or misses a part.

It never starts a coding agent, and it never calls the model. For each test run, a stand-in claude
and a stand-in codex come first on PATH. Each stops at once.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE / "lab"
RECORD = "run-1-record.md"
PROMPT = "run1-prompt.txt"
DONE_WHEN = "tests/test_schema.py"
# The last commit of the start, from lab-states/build_lab.py: the state before run 1.
START = "Record the data-rules check, passed, before any AI tool"
# Files that are not the run's: your report, the prompt, and the lab's agent configuration. Claude Code
# writes .claude/settings.local.json when you let it do a thing without a question next time.
NOT_THE_RUN = {RECORD, PROMPT, ".claude/settings.json", ".claude/settings.local.json"}
LABELS = ["Done", "Proof"]
COUNT = re.compile(r"(\d+) (passed|failed|errors?|skipped|xfailed|xpassed)\b")
# One pytest summary, such as "1 failed, 21 passed, 1 warning".
SUMMARY = re.compile(r"\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed)\b"
                     r"(?:,? \d+ (?:passed|failed|errors?|skipped|xfailed|xpassed|warnings?)\b)*")

# The notebook's lines that each answer rests on, and the steps that give it. The steps have the same
# numbers in the notebook and in the README.
RUN_1 = ("Day 5, the opening, under \"Today's runs build the extractor: a note in, five fields out.\": \"Run 1 "
         "writes its schema, run 2 the extractor.\"")
RUN_IT = "Section 5.2, list \"For every run, yourself\": \"Run the done-when in your own terminal\"."
TESTS_FIRST = "Section 5.2, list \"For every run, yourself\": \"Read the test files' diff first\"."
DONE_WHEN_LINE = ("Section 5.1, run 1's Done-when: \"one output that must fail (amount_in_question missing) and one "
                  "that must pass with amount_in_question null\".")
EVIDENCE = "Section 5.2, list \"Have it show evidence\": \"The command it ran, and what it returned\"."
REPORT = "Section 5.2, list \"For every run, yourself\": \"The report: done, proof, scope, not verified\"."
COMMITTED = "Section 5.2, the answer to its Check: \"the commit and the stored result are evidence.\""
TABLE = "the table in step 3"


def git(*args):
    return subprocess.run(["git", *args], cwd=LAB, capture_output=True, text=True)


def stop(message):
    print("Not yet: " + message)
    sys.exit(1)


# --- What the run left, and what its tests hold ----------------------------------------------

def start_commit():
    for line in git("log", "--format=%H %s").stdout.splitlines():
        sha, _, subject = line.partition(" ")
        if subject == START:
            return sha
    return None


def run_files(start):
    """Each file that run 1 added, changed or removed since the start, committed or not."""
    changed = git("diff", "--name-only", "-z", start).stdout.split("\0")
    new = git("ls-files", "--others", "--exclude-standard", "-z").stdout.split("\0")
    return sorted({path for path in changed + new if path} - NOT_THE_RUN)


def without_stand_ins(folder):
    """The environment of each test run: a claude and a codex that stop at once come first on PATH."""
    for name in ("claude", "codex"):
        path = folder / name
        path.write_text("#!/bin/sh\necho 'The done check starts no model and no coding agent.' >&2\nexit 1\n")
        path.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = str(folder) + os.pathsep + env.get("PATH", "")
    env.pop("FORCE_COLOR", None)  # A kernel sets it. The check reads plain text.
    env.update({"NO_COLOR": "1", "PY_COLORS": "0", "PYTHONDONTWRITEBYTECODE": "1"})
    return env


def counts(line):
    """The counts of a pytest summary line, such as {"passed": 5}. It leaves out the warnings and the time."""
    found = {}
    for number, word in COUNT.findall(line):
        found["error" if word.startswith("error") else word] = int(number)
    return found


def shows(proof, theirs):
    """Whether the Proof shows the counts of the last line: in all its counts, or in one summary in it.
    A Proof can also give the count of a run of your own, after a change to the schema."""
    if all(counts(proof).get(word) == number for word, number in theirs.items()):
        return True
    return any(all(counts(found.group(0)).get(word) == number for word, number in theirs.items())
               for found in SUMMARY.finditer(proof))


def outcomes(xml):
    """Each test of a pytest report in JUnit XML, by its class and name: passed, failed or skipped."""
    found = {}
    try:
        root = ElementTree.parse(str(xml)).getroot()
    except (OSError, ElementTree.ParseError):
        return found
    for case in root.iter("testcase"):
        tags = {child.tag for child in case}
        outcome = "failed" if tags & {"failure", "error"} else "skipped" if "skipped" in tags else "passed"
        found[(case.get("classname", ""), case.get("name", ""))] = outcome
    return found


def run_done_when(where, env, xml):
    """Run the done-when in `where`: its exit code, its last line without the time, and each test's outcome."""
    try:
        run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--color=no",
                              f"--junitxml={xml}", DONE_WHEN],
                             cwd=where, env=env, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return 1, "no result after 180 seconds", {}
    lines = [line.strip(" =") for line in run.stdout.splitlines() if line.strip(" =")]
    last = re.sub(r"\s+in\s+[\d.]+s\b.*$", "", lines[-1]) if lines else "no output"
    return run.returncode, last, outcomes(xml)


def has_amount(node):
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict) and "amount_in_question" in properties:
            return True
        return any(has_amount(value) for value in node.values())
    return isinstance(node, list) and any(has_amount(value) for value in node)


def not_required(node):
    """The first change: amount_in_question leaves every list of required fields."""
    if isinstance(node, dict):
        if isinstance(node.get("required"), list):
            node["required"] = [name for name in node["required"] if name != "amount_in_question"]
        for value in node.values():
            not_required(value)
    elif isinstance(node, list):
        for value in node:
            not_required(value)


def never_null(node):
    """The second change: amount_in_question can be an integer only."""
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict) and "amount_in_question" in properties:
            properties["amount_in_question"] = {"type": "integer"}
        for value in node.values():
            never_null(value)
    elif isinstance(node, list):
        for value in node:
            never_null(value)


def required_in_all_of(node):
    """The first change in form only: amount_in_question leaves each list of required fields, and an
    "allOf" requires it. The schema accepts the same outputs."""
    if isinstance(node, dict):
        for value in list(node.values()):
            required_in_all_of(value)
        required = node.get("required")
        if isinstance(required, list) and "amount_in_question" in required:
            node["required"] = [name for name in required if name != "amount_in_question"]
            all_of = node.get("allOf")
            node["allOf"] = (all_of if isinstance(all_of, list) else []) + [{"required": ["amount_in_question"]}]
    elif isinstance(node, list):
        for value in node:
            required_in_all_of(value)


def type_in_any_of(node):
    """The second change in form only: the schema of amount_in_question goes into an "anyOf". The
    schema accepts the same outputs."""
    if isinstance(node, dict):
        for value in list(node.values()):
            type_in_any_of(value)
        properties = node.get("properties")
        if isinstance(properties, dict) and "amount_in_question" in properties:
            properties["amount_in_question"] = {"anyOf": [properties["amount_in_question"]]}
    elif isinstance(node, list):
        for value in node:
            type_in_any_of(value)


# Each part of the done-when (section 5.1), by name: the change to the schema that a test of it must catch, the
# change in form only that such a test must pass, what is missing in plain words, and how to find the test,
# in the words of the table in step 3.
PARTS = [("must-fail", not_required, required_in_all_of,
          "no test in tests/test_schema.py expects an error from the schema in schema/ when an output lacks "
          "amount_in_question.",
          "expects an error when an output lacks amount_in_question"),
         ("null-passes", never_null, type_in_any_of,
          "no test in tests/test_schema.py sets amount_in_question to None and expects no error from the schema "
          "in schema/.",
          "sets amount_in_question to None, Python's null, and expects no error")]
# The label in Proof that each part's test name follows, as the table in step 3 gives it.
PROOF_LABELS = {"must-fail": "Must fail", "null-passes": "Null passes"}
# A must-fail test can take out each required field in turn, as Codex's run 1 does, and name no field.
ANY_FIELD = {"must-fail": " A test that takes out each required field in turn counts too: amount_in_question is one "
                          "of them."}


def schemas(root):
    """The JSON files in schema/ that give amount_in_question a schema."""
    found = []
    for path in sorted((root / "schema").rglob("*.json")) if (root / "schema").is_dir() else []:
        try:
            if has_amount(json.loads(path.read_text())):
                found.append(path.relative_to(root))
        except (OSError, ValueError):
            continue
    return found


def run_changed(copy, files, change, env, xml):
    """Each test's outcome on the copy, after one change to each schema file. Then the files are as before."""
    kept = {path: (copy / path).read_text() for path in files}
    for path in files:
        data = json.loads(kept[path])
        change(data)
        (copy / path).write_text(json.dumps(data))
    found = run_done_when(copy, env, xml)[2]
    for path, text in kept.items():
        (copy / path).write_text(text)
    return found


def parts_held(env, tmp):
    """For each part of the done-when, the tests that hold it. Each passes on a copy of lab/. After the
    change to the schema of that part, it fails or is not there. A case from the list of required
    fields is not there after the first change. After the change in form only, it does not fail. A
    test that fails then reads the form of the schema, such as its list of required fields, and no
    output. None: the check cannot tell. Then the schema of the run is not a JSON file in schema/, or
    the tests do not pass on a copy."""
    copy = tmp / "lab"
    shutil.copytree(LAB, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    files = schemas(copy)
    if not files:
        return None
    code, _, before = run_done_when(copy, env, tmp / "copy.xml")
    if code != 0 or not before:
        return None
    held = {}
    for name, change, same, _, _ in PARTS:
        after = run_changed(copy, files, change, env, tmp / f"{name}.xml")
        caught = {test for test, outcome in before.items()
                  if outcome == "passed" and after.get(test, "failed") == "failed"}
        form = run_changed(copy, files, same, env, tmp / f"{name}-form.xml") if caught else {}
        held[name] = {test for test in caught if form.get(test) != "failed"}
    return held


# --- Your report ---------------------------------------------------------------------------------

def record_fields(text):
    fields, current = {}, None
    for line in text.splitlines():
        label = next((name for name in LABELS if line.startswith(name + ":")), None)
        if label:
            current = label
            fields[label] = line[len(label) + 1:].strip()
        elif current and line.strip():
            fields[current] = (fields[current] + " " + line.strip()).strip()
    return fields


def verdict(text):
    """met, not met, or None, from the first words of Done."""
    words = text.lower().lstrip(" \t*_`>-:.")
    if re.match(r"(not\s+met|no)\b", words):
        return "not met"
    if re.match(r"(met|yes)\b", words):
        return "met"
    return None


def named_tests(text, tests):
    """The tests that the text names: a test by its name, or one case of a test by its name and [...]."""
    found = set()
    for test in tests:
        name = test[1]
        base = name.split("[")[0]
        if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text) or \
                re.search(r"(?<!\w)" + re.escape(base) + r"(?![\w\[]|\.py\b)", text):
            found.add(test)
    return found


def after_label(proof, label):
    """The Proof's text after the label and its colon, up to the next label. The whole Proof when the label is
    not there."""
    labels = "|".join(re.escape(name) + r"\s*:" for name in PROOF_LABELS.values())
    found = re.search(re.escape(label) + r"\s*:(.*?)(?=" + labels + r"|$)", proof, re.I | re.S)
    return found.group(1) if found else proof


# --- The check -------------------------------------------------------------------------------------

def main():
    if not (LAB / ".git").is_dir():
        stop("there is no repository lab/ yet. Run python3 ~/practice/reset.py direct-run-one.")
    start = start_commit()
    if start is None:
        stop("lab/ no longer holds the course team's commits. Run python3 ~/practice/reset.py direct-run-one.")
    problems = []
    files = run_files(start)
    met = last = held = None
    code = 0
    tests = {}
    if not files:
        problems.append(f"lab/ holds no file of run 1 yet. Start your agent in a terminal in lab/, as step 2 says. "
                        f"Paste all of {PROMPT}. {RUN_1}")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            env = without_stand_ins(tmp)
            code, last, tests = run_done_when(LAB, env, tmp / "lab.xml")
            if code != 0:
                met = False
            else:
                held = parts_held(env, tmp)
                met = None if held is None else all(held.values())

    done = None
    if not (LAB / RECORD).is_file():
        problems.append(f"{RECORD} is not in lab/. Copy ../files/{RECORD} into lab/ again.")
    else:
        fields = record_fields((LAB / RECORD).read_text())
        missing = [name for name in LABELS if name not in fields]
        if missing:
            problems.append(f"{RECORD} has no line that starts with " + " or ".join(m + ":" for m in missing)
                            + f". Write the lines of {TABLE}, each at the start of its line. {REPORT}")
        problems.extend(report_problems(fields, met, code, last, tests, held))
        done = verdict(fields.get("Done", ""))

    if files and done == "not met" and met is not True:
        problems.append("run 1 does not meet its done-when, as your report says. Direct and check run 1 again, as "
                        f"step 2 says. {TESTS_FIRST}")
    elif files and met is not False:
        # A run that fails its done-when, or misses a part, is not one to accept: no line asks for its commit.
        left = [line[3:] for line in git("status", "--porcelain", "--untracked-files=all", "--", "schema",
                                         "tests").stdout.splitlines()]
        if left:
            problems.append("these files are not in a commit as they are now: " + ", ".join(left) + ". Stage each "
                            f"one, as step 2 does. Then commit, as step 3 says. {COMMITTED}")

    if problems:
        print(f"Not yet: {len(problems)} left.")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    if met:
        print("Done: run 1 meets its done-when, your Proof names the test of each part, and run 1 is in a commit.")
    else:
        print("Done: your report says that run 1 meets its done-when. The check cannot change the schema of this "
              "run, so your Done stands. Run 1 is in a commit.")


def report_problems(fields, met, code, last, tests, held):
    """The items that your report still needs. A label that is missing has its own line in main()."""
    problems = []
    done = verdict(fields.get("Done", ""))
    if "Done" in fields:
        if not fields["Done"]:
            problems.append(f"{RECORD}: Done is empty. Write met or not met, as {TABLE} says. {DONE_WHEN_LINE}")
        elif done is None:
            problems.append(f"{RECORD}: Done does not start with met or not met. Write it as {TABLE} does. {REPORT}")
        elif done == "met" and met is False and code != 0:
            problems.append(f"{RECORD}: Done says met, but the done-when fails on run 1: {last}. Write not met, "
                            f"as {TABLE} says. {RUN_IT}")
        elif done == "met" and met is False:
            plain = next(p for p in PARTS if not held[p[0]])[3]
            problems.append(f"{RECORD}: Done says met, but {plain} So run 1 misses a part of the done-when. "
                            f"Write not met, as {TABLE} says. {DONE_WHEN_LINE}")
        elif done == "not met" and met is True:
            problems.append(f"{RECORD}: Done says not met, but run 1 passes, and a test holds each part of the "
                            f"done-when. Write met, as {TABLE} says. {DONE_WHEN_LINE}")
    proof = fields.get("Proof")
    if proof == "":
        problems.append(f"{RECORD}: Proof is empty. Write the command, its last line and the two test names, as "
                        f"{TABLE} gives them. {EVIDENCE}")
    elif proof is not None and last is not None:
        theirs = counts(last)
        if "pytest" not in proof or "test_schema.py" not in proof:
            problems.append(f"{RECORD}: Proof does not name the command of the done-when, pytest {DONE_WHEN}. "
                            f"Write it as {TABLE} does. {EVIDENCE}")
        elif (theirs and not shows(proof, theirs)) or (not theirs and last.lower() not in proof.lower()):
            problems.append(f"{RECORD}: Proof does not show the last line that the done-when prints on run 1 "
                            f"now: {last}. Run the done-when again, as step 2 says. Copy its last line. The time can "
                            f"differ. {EVIDENCE}")
        # The test names count with every Done, an empty or unclear one too, except where the check asks for a new run.
        if met is True or (met is None and done != "not met"):
            if held is not None:
                for name, _, _, _, find in PARTS:
                    label = PROOF_LABELS[name]
                    if not named_tests(after_label(proof, label), tests) & held[name]:
                        problems.append(f"{RECORD}: Proof names no test after \"{label}:\" that {find}. Find it in "
                                        f"{DONE_WHEN}.{ANY_FIELD.get(name, '')} Write the name after def, as {TABLE} "
                                        f"says. {EVIDENCE}")
            elif not any(tests.get(test) == "passed" for test in named_tests(proof, tests)):
                problems.append(f"{RECORD}: Proof names no test of {DONE_WHEN} that passes. Write the name after "
                                f"def of each of the two tests, as {TABLE} says. {EVIDENCE}")
    return problems


if __name__ == "__main__":
    main()
