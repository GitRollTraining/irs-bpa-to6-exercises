"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads lab/run2-prompt.txt, your directing prompt for run 2, one part at a time.

- Context: each path is in lab/. The paths point to each file that the function or its tests use.
- Constraints: the check tries your rules on the files that an agent can change in run 2. The rules
  must let the agent add the two files of the Goal. They must keep the files of run 1 and the
  recorded replies as they are. They must also say that the tests call no model, and that no note
  text goes into a log. Run 1's "Do not call any model." does not pass: the Goal's function calls it.
- Done-when: the check runs your command on the course's run 2 (lab-states/run2), in a new lab that
  it builds as the reset does. The command must pass there. Then the check runs it on two wrong runs
  (files/wrong-run-2/). The command must fail on each of them. The check also reads the reply that
  must fail, and the note that names no amount.

A stand-in for the route to the model is first on the PATH of your command, so the command cannot
reach the model. The check starts no coding agent and needs no network. The class talks the wording
of your prompt through.
"""
import fnmatch
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from start import PROMPT, RUN2_INPUTS, STATES, build_start  # noqa: E402

LAB = HERE / "lab"
WRONG = HERE / "files" / "wrong-run-2"
PARTS = ["Goal", "Context", "Constraints", "Done-when"]
GOAL_FILES = ["extractor.py", "tests/test_extractor.py"]
RUN1_FILES = ["schema/output.schema.json", "tests/test_schema.py"]
RECORDED = [path for path in RUN2_INPUTS if path.startswith("tests/recorded/")]
RECORDED_NOTES = {pathlib.Path(path).stem for path in RECORDED}
# The files that the function or its tests use: the paths that Context must point to.
NEEDED = ["model.py", "prompts/system.txt", "schema/output.schema.json", "tests/recorded/"]
# The lab's notes that name no amount, from the course's labels. notes/README.md gives their number, 16.
NO_AMOUNT = {"0102", "0104", "0107", "0110", "0112", "0116", "0119", "0121", "0124", "0127", "0129",
             "0131", "0134", "0136", "0138", "0140"}
EXTENSIONS = ("py", "md", "txt", "json", "jsonl", "toml", "cfg", "ini", "yaml", "yml", "csv", "log")

# Each miss names the step that gives the line, and the notebook line it rests on, with its section and heading.
STEP = "step 2"
RUNS = 'The Opening, under "Today\'s runs build the extractor": '
RUN1 = "Section 5.1, run 1's table, "
AT_FILES = 'Section 5.1, under "A one-line task is a wish": "Reference specific files".'
AT_CONSTRAINTS = (RUN1 + 'Constraints: "Do not call any model. Do not edit anything outside schema/ and tests/. '
                  'Do not log note text."')
AT_RECORDED = RUNS + '"tested on model replies recorded earlier".'
AT_NO_AMOUNT = RUNS + '"A note with no amount: amount_in_question is null".'
AT_COMMAND = 'Section 5.1, under "Only the done-when": "the part someone who did not watch can check from a command".'
AT_MUST_FAIL = RUN1 + 'Done-when: "it includes one output that must fail (amount_in_question missing)".'
AT_SCOPE = RUN1 + 'Constraints: "Do not edit anything outside schema/ and tests/."'
AT_TYPES = RUN1 + 'Constraints: "amount_in_question is an integer or null, and is always present."'
AT_LOG = RUN1 + 'Constraints: "Do not log note text."'

COURSE_RUN = "~/practice/lab-states/run2/"

NEGATION = re.compile(r"\b(?:do not|don't|does not|doesn't|never|must not|mustn't|may not|cannot|can't|"
                      r"should not|shouldn't|no)\b", re.I)
EDIT = re.compile(r"\b(?:edit|chang|modif|touch|alter|writ|rewrit|overwrit|delet|remov|renam|mov|updat|add|"
                  r"creat|replac|make)\w*", re.I)
# The "only" of "read-only" is not a marker. KEEP below reads "read-only" as a rule that keeps the files.
ALLOW = re.compile(r"\b(?:outside|except|apart from|besides|(?<!read-)(?<!read )only|no other|nothing else|"
                   r"anything else|any other|every other|everything else|other(?:\s+\w+)?\s+than)\b|"
                   r"\bbut(?=\s+(?:not\s+)?[\w.~-]*[/.]\w)", re.I)
# These name the other files only in a rule that names no path itself: "Leave the rest unchanged."
OTHERS = re.compile(r"\b(?:the rest|all other|other files?)\b", re.I)
# "Only the course team edits X": only a person may change X, so the agent may not.
ONLY_A_PERSON = re.compile(r"\s+(?:a\s+|the\s+)?(?:course\s+)?(?:team|person|people|human|humans|you|we|i|"
                           r"reviewer|developer)\b", re.I)
KEEP = re.compile(r"\b(?:unchanged|untouched|read-only|read only|as (?:it|they) (?:is|are)|"
                  r"(?:stay|stays) the same)\b", re.I)
PRONOUN = re.compile(r"\b(?:it|them|these|those|this|that)\b", re.I)
# When the last verb before the first path is one of these, the clause tells what the function or the tests do
# with the file. It is not a rule on which files the agent may change: "The function returns only a reply that
# matches schema/output.schema.json."
USE = re.compile(r"\b(?:return|give|validate|match|accept|pass|send|use|call|check)(?:s|es|d|ed|ing)?\b|"
                 r"\b(?:giving|validating|using)\b", re.I)
FAIL = re.compile(r"\b(?:fail\w*|rais\w*|reject\w*|refus\w*)\b", re.I)
# "no test fails" and "must not fail" name no reply that must fail.
NOT_FAIL = re.compile(r"\b(?:no\s+tests?|nothing|none)\s+(?:must\s+|should\s+|may\s+|will\s+|can\s+)?fail\w*|"
                      r"\b(?:not|never)\s+(?:fail|rais|reject|refus)\w*", re.I)
# The words that name a reply that must fail: a reply, an output, JSON, a field.
REPLY = re.compile(r"\b(?:repl(?:y|ies)|outputs?|responses?|json|cases?|answers?|fields?|tax_year|form|issue|"
                   r"amount_in_question|next_action)\b", re.I)
# A command starts with one of these words. "pytest." at the end of a sentence is a command too.
COMMAND_START = re.compile(r"(?<![\w./-])(?:python3|python|pytest|git)(?![\w-]|\.\w)")
QUOTE_MARKS = "\"'‘’“”"


def write_line(part):
    """The step that gives the line to write."""
    return f"Write the {part} line from {STEP}."


def listed(items):
    """a, b and c"""
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


# --- Reading the prompt ------------------------------------------------------------------------

def read_parts(text):
    """The text of each part, by its label at the start of a line: {"Goal": ..., "Context": ...}."""
    label = re.compile(r"^\s*[*_#>-]*\s*(goal|context|constraints|done[- ]when)\s*[*_]*\s*:(.*)$", re.I)
    names = {"goal": "Goal", "context": "Context", "constraints": "Constraints", "done-when": "Done-when",
             "done when": "Done-when"}
    parts, current = {}, None
    for line in text.splitlines():
        found = label.match(line)
        if found:
            current = names[found.group(1).lower()]
            parts.setdefault(current, []).append(found.group(2))
        elif current:
            parts[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in parts.items()}


def sentences(text):
    """The sentences of a part: a new line, a semicolon, or a full stop before a new sentence ends one."""
    found = []
    for line in text.splitlines():
        for piece in re.split(r";|(?<=[.!?])\s+(?=[A-Z0-9`\"'(])", line):
            if piece.strip():
                found.append(piece.strip())
    return found


def clauses(sentence):
    """The parts of a sentence that a comma and "and", "or" or "but" join, or that a new rule starts."""
    pattern = (r",\s*(?:and|or|but|while)\s+|\s+(?:and|but)\s+(?=(?:do not|don't|never|must not|may not|"
               r"keep|leave)\b)")
    return [piece for piece in re.split(pattern, sentence, flags=re.I) if piece.strip()]


def path_tokens(text, top):
    """The paths in a piece of text, as written from the top of lab/. A word with no slash and no file
    extension is not a path. A slash between two plain words, as in "and/or", is not a path either."""
    found = []
    for raw in re.findall(r"[^\s`'\"(),;:<>\[\]{}]+", text):
        if "://" in raw or raw.startswith("http"):
            continue
        token = re.sub(r"['’]s$", "", raw.rstrip(".!?"))
        while token.startswith("./"):
            token = token[2:]
        if token.startswith("/") and not token.startswith("//"):
            token = token[1:]
        if not token:
            continue
        has_extension = re.search(r"\.(?:%s|\*)$" % "|".join(EXTENSIONS), token) is not None
        first = token.split("/", 1)[0]
        if has_extension or ("/" in token and (token.endswith("/") or first in top or first == "~")):
            found.append(token)
    return found


def in_lab(path):
    try:
        return any(LAB.glob(path)) if "*" in path else (LAB / path).exists()
    except (ValueError, NotImplementedError, OSError):  # a pattern that pathlib cannot read
        return False


def uses_file(clause, paths):
    """True when the last verb before the first path of the clause is a verb of USE, not one of EDIT."""
    first = min((clause.find(path) for path in paths if path in clause), default=-1)
    if first <= 0:
        return False
    verbs = [(found.start(), True) for found in USE.finditer(clause[:first])]
    verbs += [(found.start(), False) for found in EDIT.finditer(clause[:first])]
    return bool(verbs) and max(verbs)[1]


def covers(rule, target):
    """True when the path or folder rule holds target, such as tests/ for tests/test_schema.py."""
    rule = rule.rstrip("/")
    if "*" in rule:
        return fnmatch.fnmatch(target, rule) or fnmatch.fnmatch(target, rule + "/*")
    return target == rule or target.startswith(rule + "/")


# --- Context -----------------------------------------------------------------------------------

def context_problems(context, top):
    problems = []
    named = path_tokens(context, top)
    missing = [path for path in dict.fromkeys(named) if path not in GOAL_FILES and not in_lab(path)]
    if missing:
        problems.append(f"Context names {listed(missing)}, which lab does not hold. Each path starts at the top of "
                        f"lab. {write_line('Context')} {AT_FILES}")
    unnamed = [need for need in NEEDED
               if not any(covers(path, need.rstrip("/")) or covers(need, path.split("*")[0].rstrip("/"))
                          for path in named if need != "model.py" or path == "model.py")]
    if unnamed:
        problems.append(f"Context does not name {listed(unnamed)}, which the function or its tests use. "
                        f"{write_line('Context')} {AT_FILES}")
    return problems


# --- Constraints -------------------------------------------------------------------------------

def scope(constraints, top):
    """The rules on which files the agent may change: (allow, deny, named). allow holds groups of paths, and a
    file may change only if a group covers it. deny holds (path, exceptions) pairs. named is True when a rule
    names files that the agent may change, but not that it may change only those: "Edit extractor.py.\""""
    allow, deny = [], []
    last_positive = []
    for sentence in sentences(constraints):
        positive, kind, previous = [], None, []
        for clause in clauses(sentence):
            paths = path_tokens(clause, top)
            if not paths and PRONOUN.search(clause):
                paths = previous  # "Read schema/, but do not edit it."
            use = uses_file(clause, paths)
            marker = None if use else ALLOW.search(clause)
            if marker and marker.group(0).lower() == "only" and ONLY_A_PERSON.match(clause[marker.end():]):
                deny.extend((path, []) for path in paths)  # "Only the course team edits X."
                kind = "deny"
            elif marker:
                before, after = clause[:marker.start()], clause[marker.end():]
                before_paths, after_paths = path_tokens(before, top), path_tokens(after, top)
                if marker.group(0).lower() == "only" and not after_paths:
                    allow.append(before_paths)  # "Edit X and Y only."
                elif before_paths and NEGATION.search(before) and not KEEP.search(before):
                    deny.extend((path, after_paths) for path in before_paths)  # "Do not edit X except Y."
                elif after_paths or before_paths:
                    allow.append(after_paths or before_paths)
                else:
                    allow.append(positive or last_positive)  # "..., and nothing else."
                kind = "allow"
            elif not paths and OTHERS.search(clause) and (KEEP.search(clause) or NEGATION.search(clause)):
                allow.append(positive or last_positive)  # "Leave the rest unchanged."
                kind = "allow"
            elif KEEP.search(clause) or (NEGATION.search(clause) and EDIT.search(clause)):
                deny.extend((path, []) for path in paths)
                kind = "deny"
            elif EDIT.search(clause) and not use:
                positive.extend(paths)
                kind = "positive"
            elif paths and kind == "deny" and not use:
                deny.extend((path, []) for path in paths)  # a list that a comma and "and" go on with
            elif paths and kind == "allow" and not use:
                allow[-1] = allow[-1] + paths
            previous = paths or previous
        last_positive = positive or last_positive
    return [group for group in allow if group], deny, bool(last_positive)


def may_change(target, allow, deny):
    for path, exceptions in deny:
        if covers(path, target) and not any(covers(exception, target) for exception in exceptions):
            return False
    return not allow or any(covers(path, target) for group in allow for path in group)


def says(text, *patterns):
    return any(all(re.search(pattern, sentence, re.I) for pattern in patterns) for sentence in sentences(text))


def constraint_problems(constraints, done_when, top):
    problems = []
    allow, deny, named = scope(constraints, top)
    if not allow and not deny and named:
        problems.append("Constraints name files that the agent may change, but not that it may change only those. "
                        f"{write_line('Constraints')} {AT_SCOPE}")
    elif not allow and not deny:
        problems.append(f"Constraints do not say which files the agent may change. {write_line('Constraints')} "
                        f"{AT_SCOPE}")
    else:
        blocked = [path for path in GOAL_FILES if not may_change(path, allow, deny)]
        if blocked:
            problems.append(f"Constraints do not let the agent add {' and '.join(blocked)}, which the Goal asks for. "
                            f"{write_line('Constraints')} {AT_SCOPE}")
        if any(may_change(path, allow, deny) for path in RUN1_FILES):
            problems.append("Constraints let the agent change a file of run 1: schema/output.schema.json or "
                            f"tests/test_schema.py. {write_line('Constraints')} {AT_SCOPE}")
        if any(may_change(path, allow, deny) for path in RECORDED):
            problems.append("Constraints let the agent change the replies in tests/recorded/. "
                            f"{write_line('Constraints')} {AT_RECORDED}")
    both = constraints + "\n" + done_when
    negation = r"\b(?:no|not|never|without|don't|nothing)\b"
    tests = r"\btests?\b"
    call = r"\b(?:call|reach|use|send|run|invok|contact)\w*"
    model = r"\bmodels?\b(?![.-]\w)"
    # "The tests call no model.", "The tests must not call model.py.", "Tests give a fake ask().", but never
    # "Do not edit model.py.", which is a rule on a file. The rule names the tests: the Goal's function calls the model.
    no_model = (says(both, model, negation, tests)
                or says(both, r"\bmodel\.py\b|\bmodel\.ask\b|\bask\(\)|\bclaude\b|\broute\b", negation, call, tests)
                or says(both, r"\b(?:fake|stub|stand-in|mock)\w*", r"\b(?:ask|model|claude|route)\b"))
    recorded = any(re.search(tests, sentence, re.I)
                   and re.search(r"\brecorded\b|tests/recorded", sentence, re.I)
                   and not (NEGATION.search(sentence) and EDIT.search(sentence)) for sentence in sentences(both))
    # Run 1's "Do not call any model." keeps the Goal's function from the model too.
    no_call_at_all = any(re.search(model + r"|\bmodel\.py\b", sentence, re.I) and re.search(negation, sentence, re.I)
                         and re.search(call, sentence, re.I)
                         and not re.search(tests + r"|\bfunction\b|\bextractor\b", sentence, re.I)
                         for sentence in sentences(constraints))
    if no_call_at_all:
        problems.append("Constraints say that nothing calls a model, but the Goal's function sends each note to the "
                        f"model. Only the tests must call no model. {write_line('Constraints')} {AT_RECORDED}")
    elif not (no_model or recorded):
        problems.append(f"Constraints do not say that the tests call no model. {write_line('Constraints')} "
                        f"{AT_RECORDED}")
    # The log rule keeps note text out: "Do not log note text.", "Keep note text out of all logs.", "Keep note text
    # out of logging.", "Logs must not include note content.", "Logging must exclude note text.", "Log only the note
    # number." "Log the note text, not the note number." does not: its "not" is on the number.
    no_text = (r"\b(?:no|not|never|without|don't|exclud\w*|redact\w*|omit\w*|leaves?\s+out)\b[^.,;]*"
               r"\b(?:log\w*|text|contents?|words?)\b"
               r"|\blog\w*\b[^.,;]*\btext\b[^.,;]*\b(?:not|never)\b|\bout of\b[^.,;]*\blog(?:s|ging)?\b"
               r"|\bonly\b[^.,;]*\b(?:numbers?|identifiers?|ids?)\b|\b(?:numbers?|identifiers?|ids?)\s+only\b")
    if not says(constraints, r"\blog(?:s|ged|ging)?\b", no_text):
        problems.append(f"Constraints do not say that no log holds note text. {write_line('Constraints')} {AT_LOG}")
    return problems


# --- Done-when ---------------------------------------------------------------------------------

def commands_in(done_when):
    """The commands in Done-when. A text in backticks is a command if it starts with python3, python, pytest
    or git. With no such text, each command runs up to the first plain word after it, such as "passes". A
    closing quotation mark also ends a command: "python3 -m pytest -q tests/" passes."""
    quoted = [span.strip() for span in re.findall(r"`([^`]+)`", done_when) if COMMAND_START.match(span.strip())]
    if quoted:
        return quoted
    found = []
    for line in done_when.splitlines():
        end = 0
        for start in COMMAND_START.finditer(line):
            if start.start() < end:
                continue
            words, pos = [start.group(0)], start.end()
            while True:
                gap = re.match(r"\s+", line[pos:])
                if not gap:
                    break
                rest = line[pos + gap.end():]
                quote = re.match(r"(['\"]).*?\1", rest)
                token = quote.group(0) if quote else (re.match(r"\S+", rest).group(0) if rest else "")
                if not token:
                    break
                bare = token.rstrip(".,;:!?)")
                closing = not quote and bare[-1:] in QUOTE_MARKS  # the end of a command in quotation marks
                if closing:
                    bare = bare.rstrip(QUOTE_MARKS).rstrip(".,;:!?)")
                if not bare:
                    break
                if not (quote or bare.startswith("-") or re.search(r"[/.=:]", bare)
                        or re.fullmatch(r"[A-Z0-9_^~]+", bare)
                        or (words[-1] in ("-m", "-k") and re.fullmatch(r"\w+", bare))
                        or (words[0] == "git" and len(words) == 1 and re.fullmatch(r"[a-z-]+", bare))):
                    break
                words.append(bare)
                pos += gap.end() + len(token)
                if bare != token:
                    break  # a comma, a full stop or a closing quotation mark ends the command
            end = pos
            if len(words) > 1 or words[0] == "pytest":
                found.append(" ".join(words))
    return found


def why_it_failed(line):
    """One sentence on what a command that fails on the course's run 2 most likely got wrong, or nothing."""
    if re.search(r"not found:|no match in any of|no such file", line, re.I):
        return (" The course's run 2 does not have a file or a test that the command names. Use only the names "
                "that the Goal gives.")
    if re.search(r"expected one argument|unrecognized arguments|usage:", line, re.I):
        return " The check read only a part of the command. Put the full command between backticks (`)."
    if re.search(r"no tests ran|ran 0 tests|deselected", line, re.I):
        return " The command runs no test of the course's run 2."
    return ""


def last_line(output, folder=None):
    """The last line of a command's output, without colour codes and without the path of folder. It skips
    pytest's "(no match in any of [...])" line: the line before it names the test that is not there."""
    lines = [re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", line).strip(" =") for line in output.splitlines()]
    lines = [line for line in lines if line and not line.startswith("(no match in any of")]
    if not lines:
        return "no output"
    line = re.sub(r"\s+in [\d.]+s(?:\s+\([^)]*\))?$", "", lines[-1])
    places = {str(folder), os.path.realpath(str(folder))} if folder else set()
    for place in sorted(places, key=len, reverse=True):  # /private/var/... before /var/... on macOS
        line = line.replace(place + os.sep, "")
    return line


def run(commands, folder, stand_ins):
    """Run each command in folder, as you run it in lab. It gives three values: True when each command ends
    with 0, the last line, and whether a command called the model. The stand-ins are first on PATH: a
    claude that fails, and python3, python and pytest that run this Python."""
    called = stand_ins / "model-called"
    if called.exists():
        called.unlink()
    env = {key: value for key, value in os.environ.items() if key not in ("FORCE_COLOR", "PYTEST_ADDOPTS")}
    env.update({"PATH": f"{stand_ins}{os.pathsep}{os.environ.get('PATH', '')}", "PY_COLORS": "0", "NO_COLOR": "1",
                "GIT_PAGER": "cat", "PAGER": "cat", "GIT_TERMINAL_PROMPT": "0"})
    shown = ""
    for command in commands:
        try:
            done = subprocess.run(command, shell=True, cwd=folder, env=env, stdin=subprocess.DEVNULL,
                                  capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return False, "it did not end in 120 seconds", called.exists()
        line = last_line(done.stdout + "\n" + done.stderr, folder)
        # Before Python 3.12, unittest ends with 0 when it finds no test: such a command checks nothing.
        ran_none = re.search(r"^Ran 0 tests\b", done.stdout + "\n" + done.stderr, re.M)
        if done.returncode != 0 or ran_none:
            return False, "Ran 0 tests" if ran_none else line, called.exists()
        shown = line if line != "no output" else shown
    return True, shown or "no output", called.exists()


def make_stand_ins(folder):
    scripts = {"claude": f'#!/bin/sh\n: > "{folder / "model-called"}"\n'
                         'echo "The check never calls the model." >&2\nexit 1\n',
               "codex": '#!/bin/sh\necho "The check never starts a coding agent." >&2\nexit 1\n',
               "python3": f'#!/bin/sh\nexec "{sys.executable}" "$@"\n',
               "python": f'#!/bin/sh\nexec "{sys.executable}" "$@"\n',
               "pytest": f'#!/bin/sh\nexec "{sys.executable}" -m pytest "$@"\n'}
    for name, text in scripts.items():
        (folder / name).write_text(text)
        (folder / name).chmod(0o755)


def runs_of_run2(folder):
    """The course's run 2, as an agent leaves it in lab/ before you accept it, and the two wrong runs."""
    course = folder / "course"
    build_start(course)
    for path in GOAL_FILES:
        shutil.copy(STATES / "run2" / path, course / path)
    wrong = {}
    for name, what in (("accepts-any-reply", "accepts every reply that is JSON"),
                       ("supplies-an-amount", "supplies an amount for a note that names no amount")):
        copy = folder / name
        shutil.copytree(course, copy, symlinks=True)
        shutil.copy(WRONG / f"{name}.py", copy / "extractor.py")
        wrong[name] = (copy, what)
    return course, wrong


def names_a_failing_reply(done_when):
    """True when a sentence says that a reply must fail. It holds a fail word and a reply, an output or a field.
    The reply can also be in the sentence before, when the fail word is in a sentence that starts "it" or
    "which". "No test fails" names no reply."""
    found = sentences(done_when)
    for number, sentence in enumerate(found):
        if not FAIL.search(NOT_FAIL.sub(" ", sentence)):
            continue
        if REPLY.search(sentence) or (number and REPLY.search(found[number - 1])
                                      and re.match(r"(?:it|this|that|they|these|each|both|which)\b", sentence, re.I)):
            return True
    return False


def wrong_fail_case(done_when):
    """A reply that Done-when says must fail, but that the output schema accepts. None when Done-when names a
    reply that the schema refuses, or a reply that the check cannot read."""
    accepted = None
    for sentence in sentences(done_when):
        for clause in re.split(r",\s*(?:and|but|while)\s+|\s+and\s+(?=(?:one|a|an|the|it|note)\b)", sentence):
            if not FAIL.search(NOT_FAIL.sub(" ", clause)):
                continue
            low = clause.lower()
            if re.search(r"\b(?:not (?:valid )?json|plain text|free text|invalid json|extra|additional|sixth|"
                         r"another field|unknown field|missing|without|lacks?|omit\w*|drop\w*|left out|absent|"
                         r"remov\w*)\b|"
                         r"\bno\s+(?:the\s+)?(?:tax_year|form|issue|amount_in_question|next_action)\b", low):
                return None
            if re.search(r"\b(?:tax_year|amount_in_question)\b.*\b(?:string|text)\b", low) or \
                    re.search(r"\b(?:tax_year|form|issue|next_action)\b.*\bnull\b", low):
                return None
            if re.search(r"\bamount_in_question\b.*\bnull\b|\bnull\b.*\bamount_in_question\b", low):
                accepted = accepted or "a reply with amount_in_question null"
            elif re.search(r"\bamount_in_question\b\W*(?:of|as|is|=|:)?\s*-?\d+\b(?![.,]\d)", low):
                # The schema takes each whole number: only the note shows that 0 is wrong for note 0102.
                accepted = accepted or "a reply with a whole number in amount_in_question"
            elif re.search(r"\b(?:form|issue|next_action)\b.*\b(?:string|text)\b", low):
                accepted = accepted or "a reply whose form, issue or next_action is text"
    return accepted


def note_problems(done_when):
    notes = {path.stem for path in (LAB / "notes").glob("*.txt")}
    named = sorted({number for number in re.findall(r"(?<!\d)\d{4}(?!\d)", done_when) if number in notes})
    no_amount = [number for number in named if number in NO_AMOUNT]
    unrecorded = [number for number in named if number not in RECORDED_NOTES]
    if not no_amount:
        start = (f"Done-when names note {' and '.join(named)}, which {'names' if len(named) == 1 else 'name'} an "
                 "amount, but no note with no amount" if named else "Done-when does not name a note with no amount")
        return [f"{start}. {write_line('Done-when')} {AT_NO_AMOUNT}"]
    if unrecorded:
        which = " and ".join(unrecorded)
        them = "it" if len(unrecorded) == 1 else "them"
        return [f"Done-when names note {which}, but tests/recorded/ has no reply for {them}. "
                f"{write_line('Done-when')} {AT_RECORDED}"]
    if not re.search(r"\bnull\b|\bNone\b", done_when):
        return [f"Done-when names note {no_amount[0]}, but not that the function must return null for it. "
                f"{write_line('Done-when')} {AT_NO_AMOUNT}"]
    return []


def done_when_problems(done_when):
    problems, passed = [], None
    commands = commands_in(done_when)
    if not commands:
        problems.append(f"Done-when names no command to run. {write_line('Done-when')} {AT_COMMAND}")
    else:
        shown = " and ".join(f'"{command}"' for command in commands)
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            stand_ins = folder / "stand-ins"
            stand_ins.mkdir()
            make_stand_ins(stand_ins)
            course, wrong = runs_of_run2(folder)
            ok, line, called = run(commands, course, stand_ins)
            if called:
                problems.append(f"your done-when calls the model, which can give a new reply on each call. It runs "
                                f"{shown}. {write_line('Done-when')} {AT_RECORDED}")
            elif not ok:
                problems.append(f"your done-when fails on the course's run 2, which does the task. It runs {shown}. "
                                f"Its last line: {line}.{why_it_failed(line)} That run 2 is in {COURSE_RUN}. "
                                f"{write_line('Done-when')} {AT_COMMAND}")
            else:
                passed = line
                # A command that names test files, but not the Goal's, runs no test of the extractor.
                joined = " ".join(commands)
                cause = (" That command does not run tests/test_extractor.py, the tests of the Goal."
                         if re.search(r"test_\w+\.py", joined) and "test_extractor.py" not in joined else "")
                for name, (copy, what) in wrong.items():
                    wrong_ok, _, _ = run(commands, copy, stand_ins)
                    if wrong_ok:
                        rule = AT_MUST_FAIL if name == "accepts-any-reply" else AT_NO_AMOUNT
                        problems.append(f"your done-when also passes on a wrong run 2, whose extractor {what}. It runs "
                                        f"{shown}.{cause} {write_line('Done-when')} {rule}")
    if not names_a_failing_reply(done_when):
        problems.append(f"Done-when does not name a reply that must fail. {write_line('Done-when')} {AT_MUST_FAIL}")
    else:
        accepted = wrong_fail_case(done_when)
        if accepted:
            problems.append(f"Done-when says that {accepted} must fail, but the output schema accepts that reply. "
                            f"{write_line('Done-when')} {AT_TYPES}")
    problems.extend(note_problems(done_when))
    return problems, passed


# --- The check ---------------------------------------------------------------------------------

def stop(message):
    print("Not yet: 1 left.")
    print("- " + message)
    sys.exit(1)


def main():
    if not (LAB / ".git").is_dir():
        stop("lab is not a repository yet. Run python3 ~/practice/reset.py directing-prompt.")
    if not (LAB / PROMPT).is_file():
        stop(f"{PROMPT} is missing. Run python3 ~/practice/reset.py directing-prompt to get it again.")
    top = {path.name for path in LAB.iterdir() if path.name != ".git"}
    parts = read_parts((LAB / PROMPT).read_text())
    problems, passed = [], None
    rules = {"Context": AT_FILES, "Constraints": AT_CONSTRAINTS, "Done-when": AT_COMMAND}
    for part in PARTS:
        if part not in parts:
            after = (f"In {STEP}, you write the {part} line after it. {rules[part]}" if part in rules
                     else "../files/run2-prompt.txt holds the Goal as supplied.")
            problems.append(f'no line starts with "{part}:". Put the label back at the start of its line. {after}')
    goal = parts.get("Goal", "")
    lost = [path for path in GOAL_FILES if path not in goal]
    if "Goal" in parts and lost:
        problems.append(f"the Goal no longer names {' and '.join(lost)}. {STEP.capitalize()} says to keep the Goal as "
                        "it is. ../files/run2-prompt.txt holds it as supplied.")
    for part, rule in rules.items():
        if part in parts and not parts[part]:
            problems.append(f'nothing follows "{part}:" in the saved file yet. {write_line(part)} {rule}')
    if parts.get("Context"):
        problems.extend(context_problems(parts["Context"], top))
    if parts.get("Constraints"):
        problems.extend(constraint_problems(parts["Constraints"], parts.get("Done-when", ""), top))
    if parts.get("Done-when"):
        found, passed = done_when_problems(parts["Done-when"])
        problems.extend(found)

    if problems:
        print(f"Not yet: {len(problems)} left.")
        print("\n".join(f"- {PROMPT}: {problem}" for problem in problems))
        sys.exit(1)
    print(f"Done: {PROMPT} has its four parts. Your done-when passed on the course's run 2, which does the task "
          f"({passed}), and failed on the two wrong runs. In one, the extractor accepts every reply that is JSON. In "
          "the other, it supplies an amount for a note that names no amount. Your Constraints keep run 1's files and "
          "the recorded replies as they are.")


if __name__ == "__main__":
    main()
