"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads your table Models and levels in docs/pull-request.md. For the extractor's model, it compares
your choice in Start with with the course's answer. For each task, it reads the level in your command
in Start with. Then it compares the levels of the two tasks with the course's answer. For each row, it
then compares Reason with the reasons that section 2.3 allows for that choice. The facts are in
docs/model-scores.md and docs/next-tasks.md. The class talks them through. Then it looks for your commit. It calls
no model and starts no coding agent.
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE / "lab"
RECORD = "docs/pull-request.md"
FOLDER = "model-and-reasoning-level"
REASONS = ("capability", "speed", "cost")
MODELS = ("haiku", "sonnet")
# The levels that docs/next-tasks.md gives, the lowest first. Both coding agents take these three.
LEVELS = ("low", "medium", "high")
# The command that starts each coding agent at a level, as docs/next-tasks.md gives it.
COMMAND = re.compile(
    r"\bclaude\b[^|`\n]*?--effort(?:\s+|=)[\"']?(?P<claude>[A-Za-z]+)"
    r"|\bcodex\b[^|`\n]*?(?:-c|--config)(?:\s+|=)[\"']?model_reasoning_effort\s*=\s*[\"']?(?P<codex>[A-Za-z]+)")
SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}")
MODEL_ROW, TASK_1, TASK_2 = "The extractor's model", "Task 1", "Task 2"
# The course's answer: sonnet for the model, and for the tasks a level for task 1 above the level for
# task 2. Then the reasons that section 2.3 allows for each answer. answers/model-and-reasoning-level/
# decisions.md gives the rule for each.
MODEL_ANSWER = "sonnet"
ALLOWED = {MODEL_ROW: {"capability"}, TASK_1: {"capability"}, TASK_2: {"speed", "cost"}}
FACTS = {MODEL_ROW: "docs/model-scores.md", TASK_1: "docs/next-tasks.md", TASK_2: "docs/next-tasks.md"}
# Shown for a choice that the course does not accept: how to decide, in the words of the table in step 2.
LOOK_AGAIN_MODEL = ("In docs/model-scores.md, find a note that haiku got wrong and sonnet did not. One such note "
                    "is enough to move up, whatever the cost. Section 2.3, row The extractor's model: \"move up only "
                    "for a failure the set shows it fixes\". The table in step 2 shows how to decide, and the Reason "
                    "for each choice.")
LOOK_AGAIN_TASKS = ("In docs/next-tasks.md, read \"How you will check its work\" for each task. The task that you "
                    "read line by line takes the lower level. Section 2.3, below its table: \"quick exchanges where "
                    "you review each result\". The task that can change the reply for any note takes the higher one. "
                    "The table in step 2 shows how to decide, and the Reason for each level.")
REASON_RULE = ("The table in step 2 gives the reason for each choice: capability for sonnet and for task 1, and "
               "speed for task 2. Section 2.3, under \"Two dials\": \"Every reason for a choice is one of three: "
               "capability, speed or cost.\"")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def stop(message):
    print("Not yet: 1 left.")
    print("- " + message)
    sys.exit(1)


def cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table(text):
    """The rows of the table Models and levels, by the start of their first cell: {row: (Start with, Reason)}."""
    lines = text.replace("’", "'").splitlines()
    start = next((n for n, line in enumerate(lines)
                  if "|" in line and [cell.lower() for cell in cells(line)] == ["choice", "start with", "reason"]),
                 None)
    if start is None:
        return None
    found = {}
    for line in lines[start + 1:]:
        if SEPARATOR.match(line):
            continue
        if "|" not in line:
            break
        row_cells = cells(line) + ["", ""]
        for row in (MODEL_ROW, TASK_1, TASK_2):
            if row_cells[0].lower().startswith(row.lower()):
                found[row] = (row_cells[1], " ".join(row_cells[2:]).strip())
    return found


def words(text):
    return re.findall(r"[a-z]+", text.lower())


def model_choice(cell):
    """The model that Start with names. Otherwise None, and what the cell still needs."""
    named = [model for model in MODELS if model in words(cell)]
    if not named:
        return None, "in Start with, write haiku or sonnet, the two models in docs/model-scores.md."
    if len(named) > 1 or "not" in words(cell):
        return None, "in Start with, write only the model that you choose."
    return named[0], None


def task_level(cell):
    """The level in the command in Start with. Otherwise None, and what the cell still needs."""
    if "<level>" in cell:
        return None, "in Start with, write low, medium or high in place of <level>."
    if re.search(r"<\s*(?:low|medium|high)\s*>", cell, re.I):
        return None, "in Start with, take away the < and > around the level."
    if re.search(r"\b(?:Claude|CLAUDE|Codex|CODEX)\b", cell) and not COMMAND.search(cell):
        return None, "in Start with, write claude or codex in lowercase, as docs/next-tasks.md does."
    levels = {(found.group("claude") or found.group("codex")).lower() for found in COMMAND.finditer(cell)}
    if not levels:
        return None, ("in Start with, write the command that starts your coding agent at the level that you "
                      "choose. docs/next-tasks.md shows the command.")
    if len(levels) > 1:
        return None, "in Start with, write one level."
    level = levels.pop()
    if level not in LEVELS:
        return None, "in Start with, write the level low, medium or high, as docs/next-tasks.md says."
    return level, None


def reason_form(reason):
    """What Reason still needs, whatever the choice is. None when Reason starts with a reason."""
    if not reason:
        return "in Reason, write capability, speed or cost."
    first = (words(reason) or [""])[0]
    if first not in REASONS:
        return "in Reason, write capability, speed or cost."
    return None


def reason_accepted(row, reason):
    """None when section 2.3 allows this reason for the course's answer in this row."""
    first = words(reason)[0]
    if first in ALLOWED[row]:
        return None
    return (f"the course does not accept {first} as the reason for your choice. Look again at the facts in "
            f"{FACTS[row]}. {REASON_RULE}")


if not (REPO / ".git").is_dir():
    stop(f"there is no repository lab/ yet. Run python3 ~/practice/reset.py {FOLDER}.")
if not (REPO / RECORD).is_file():
    stop(f"{RECORD} is missing. Run python3 ~/practice/reset.py {FOLDER} to get it again.")
rows = table((REPO / RECORD).read_text())
if rows is None:
    stop(f"{RECORD} has no table with the columns Choice, Start with and Reason. "
         f"Run python3 ~/practice/reset.py {FOLDER} to get the file again.")

problems = []
NO_ROW = "the table has no row for this choice. Put the row back, as the file had it."
EMPTY = "fill in Start with and Reason in docs/pull-request.md, as the table in step 2 says."

# The extractor's model: the choice first, then its reason.
if MODEL_ROW not in rows:
    problems.append(f"{MODEL_ROW}: {NO_ROW}")
elif not any(rows[MODEL_ROW]):
    problems.append(f"{MODEL_ROW}: {EMPTY}")
else:
    start_with, reason = rows[MODEL_ROW]
    model, needs = model_choice(start_with)
    if not needs and model != MODEL_ANSWER:
        needs = f"the course does not accept your choice in Start with. {LOOK_AGAIN_MODEL}"
    needs = needs or reason_form(reason) or reason_accepted(MODEL_ROW, reason)
    if needs:
        problems.append(f"{MODEL_ROW}: {needs}")

# The two tasks: the level in each command, then the two levels against each other, then each reason.
levels = {}
for row in (TASK_1, TASK_2):
    if row not in rows:
        problems.append(f"{row}: {NO_ROW}")
        continue
    if not any(rows[row]):
        problems.append(f"{row}: {EMPTY}")
        continue
    start_with, reason = rows[row]
    level, needs = task_level(start_with)
    if level:
        levels[row] = level
    needs = needs or reason_form(reason)
    if needs:
        problems.append(f"{row}: {needs}")
if len(levels) == 2:
    if LEVELS.index(levels[TASK_1]) <= LEVELS.index(levels[TASK_2]):
        problems.append(f"{TASK_1} and {TASK_2.lower()}: the course does not accept your two levels. {LOOK_AGAIN_TASKS}")
    else:
        for row in (TASK_1, TASK_2):
            reason = rows[row][1]
            needs = None if reason_form(reason) else reason_accepted(row, reason)
            if needs:
                problems.append(f"{row}: {needs}")

committed = git("ls-files", "--error-unmatch", RECORD).returncode == 0 and \
    git("diff", "--quiet", "HEAD", "--", RECORD).returncode == 0
if not committed:
    problems.append(f"commit {RECORD} as it is now.")

if problems:
    print(f"Not yet: {len(problems)} left.")
    print("\n".join(f"- {problem}" for problem in problems))
    sys.exit(1)
print("Done: the course accepts the model and the two levels, and the reason for each. You committed the table.")
