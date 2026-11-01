"""The done check for this exercise. From extractor/, run: python3 ../check.py

It reads modes.md, the file that you fill in, and what Git shows in extractor/. Each Kind must be
agent, as the table in step 3 gives. Your answer under "Your run in Ask for approval" must match the
changes that Git shows since the start. It starts no coding agent, calls no model and needs no
network.
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE / "extractor"
TABLE = "modes.md"
START = REPO / ".git" / "info" / "exercise-start"
LINE = "The data-rules check passed before any AI tool ran here."
RUN = "Your run in Ask for approval"  # the heading in modes.md above the question
KINDS = ("completion", "chat", "agent")
MODES = ("Read Only", "Ask for approval", "Approve for me", "Full Access")
# The course's kind for each mode. answers/tool-modes/decisions.md gives the reason.
KIND = "agent"
STEP = "Step 3's table gives the answer and its reason."
UNDER = 'Section 4.4, under "Three kinds of tool, and they need different checks.":'
# The reason for agent and its notebook line, as step 3's table gives them. A message stands alone, so it
# names the heading in full.
KIND_WHY = ("In modes.md, each row says that Codex uses tools without your yes: it reads files and runs commands, "
            "in Read Only too. Only an agent does that: chat reaches only what you paste into it.")
KIND_LINE = f'{UNDER} "Coding agents: conversational AI models with tools".'
RESULT_LINE = '"then its result against the done-when".'


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def stop(message):
    print("Not yet: 1 left.")
    print("- " + message)
    sys.exit(1)


def plain(text):
    """A line without the marks that Markdown or a quote can add: a list mark, quotes, backticks."""
    text = re.sub(r"^\s*(?:[-*+>]|\d+[.)])\s+", "", text.strip())
    text = re.sub(r"[`*_\"'“”]", "", text)
    return " ".join(text.strip().rstrip(".").lower().split())


def rows(text):
    """The Kind cell of each mode's row in the table: {mode: cell}."""
    found, kind_at = {}, None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        names = [plain(cell) for cell in cells]
        if "kind" in names and "mode" in names:
            kind_at = names.index("kind")
            continue
        mode = next((m for m in MODES if names and names[0] == m.lower()), None)
        if mode:
            at = kind_at if kind_at is not None and kind_at < len(cells) else len(cells) - 1
            found[mode] = cells[at] if at > 0 else ""
    return found


def kinds_in(cell):
    """Each kind that the cell gives. A kind after a word such as "not" or "unlike", as in "not an agent",
    is not given."""
    words = re.findall(r"[a-z]+", cell.lower())
    given = []
    for at, word in enumerate(words):
        kind = word[:-1] if word.endswith("s") and word[:-1] in KINDS else word
        if kind not in KINDS:
            continue
        before = [w for w in words[:at] if w not in ("a", "an", "the")][-1:]
        if before and before[0] in ("not", "no", "never", "unlike", "than", "neither", "nor"):
            continue
        if kind not in given:
            given.append(kind)
    return given


def answer(text):
    """The first word after "Answer:" (or on the next line), if it is yes or no."""
    lines = [re.sub(r"[*_`]", "", line).strip() for line in text.splitlines()]
    at = next((n for n, line in enumerate(lines) if line.lower().startswith("answer:")), None)
    if at is None:
        return None, False
    rest = lines[at][len("answer:"):].strip() or next((line for line in lines[at + 1:] if line), "")
    word = re.findall(r"[a-z]+", rest.lower())[:1]
    return (word[0] if word and word[0] in ("yes", "no") else None), True


def changes(start):
    """Each file that is new, changed or removed in extractor/ since the start, committed or not.
    modes.md is not a change of Codex, also when you commit it."""
    tracked = git("diff", "--name-only", "--no-renames", "-z", start).stdout.split("\0")
    new = git("ls-files", "--others", "--exclude-standard", "-z").stdout.split("\0")
    return sorted({path for path in tracked + new if path and path != TABLE})


def result(start, changed):
    """What Git shows in README.md since the start, as the done-when in modes.md reads it, where blank
    lines do not count. met: the only change is the line, at the end. either: the same, with the line
    in another form, such as in backticks. not met: any other change."""
    if changed != ["README.md"] or not (REPO / "README.md").is_file():
        return "not met"
    diff = git("diff", "--no-color", "--no-ext-diff", "--no-renames", "-U0", start, "--", "README.md").stdout
    added, removed, in_hunk = [], [], False
    for line in diff.split("\n"):
        if line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line[:1] in ("+", "-") and line[1:].strip():
            (added if line[0] == "+" else removed).append(line[1:].strip())
    now = (REPO / "README.md").read_text(encoding="utf-8", errors="replace").splitlines()
    last = next((line.strip() for line in reversed(now) if line.strip()), "")
    if removed or len(added) != 1 or last != added[0]:
        return "not met"
    if added[0] == LINE:
        return "met"
    return "either" if plain(added[0]) == plain(LINE) else "not met"


def joined(names):
    """Read Only, Ask for approval and Full Access."""
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def rows_named(names):
    """row Read Only, or rows Read Only and Full Access."""
    return ("row " if len(names) == 1 else "rows ") + joined(names)


def main():
    if not (REPO / ".git").is_dir() or not START.is_file() or \
            git("cat-file", "-e", START.read_text().strip() + "^{commit}").returncode:
        stop("there is no repository extractor/ from the start. Run python3 ~/practice/reset.py tool-modes.")
    if not (REPO / TABLE).is_file():
        stop(f"{TABLE} is missing. Copy it again: cp ../files/{TABLE} {TABLE}")
    text = (REPO / TABLE).read_text(encoding="utf-8", errors="replace")
    problems = []

    found = rows(text)
    given = {mode: kinds_in(found[mode]) for mode in MODES if mode in found}
    empty = [mode for mode, kinds in given.items() if not kinds]
    two = [mode for mode, kinds in given.items() if len(kinds) > 1]
    wrong = {}  # each wrong kind, with the rows that give it
    for mode, kinds in given.items():
        if len(kinds) == 1 and kinds[0] != KIND:
            wrong.setdefault(kinds[0], []).append(mode)
    for mode in MODES:
        if mode not in found:
            problems.append(f"{TABLE} has no row for {mode}. Copy the row from ../files/{TABLE}.")
    if empty:
        problems.append(f"{TABLE}, {rows_named(empty)}: write agent in the Kind cell. {STEP} {KIND_LINE}")
    misses = [("write one kind only, agent.", two)] if two else []
    misses += [(f"write agent, not {kind}.", modes) for kind, modes in wrong.items()]
    for n, (what, modes) in enumerate(misses):  # the reason once, and the notebook line once a round
        why = KIND_WHY + " " if n == 0 else ""
        line = " " + KIND_LINE if n == 0 and not empty else ""
        problems.append(f"{TABLE}, {rows_named(modes)}: {what} {why}{STEP}{line}")

    start = START.read_text().strip()
    changed = changes(start)
    said, has_line = answer(text)
    if not changed:
        problems.append("Git shows no change in extractor since the start. Give Codex the request in Ask for "
                        f'approval, as step 2 says. Then fill in "Answer:" in {TABLE}.')
    elif not has_line:
        problems.append(f'{TABLE} no longer has its line "Answer:". Copy it from ../files/{TABLE}.')
    elif said is None:
        problems.append(f'{TABLE}, under "{RUN}": after "Answer:", write yes or no. {STEP}')
    else:
        truth = result(start, changed)
        others = [path for path in changed if path != "README.md"]
        # The heading in full once a round: a Kind line above gives it while a cell is empty or wrong.
        rule = ("Section 4.4, under the same heading:" if misses or empty else UNDER) + " " + RESULT_LINE
        if truth == "met" and said == "no":
            problems.append(f'{TABLE}, under "{RUN}": write yes. Git shows only the request\'s line, at the end '
                            f"of README.md. The done-when allows that, and blank lines do not count. {STEP} {rule}")
        elif truth == "not met" and said == "yes":
            what = ("a change in " + joined(others)) if others else \
                "a change in README.md other than the request's line at its end"
            problems.append(f'{TABLE}, under "{RUN}": write no. Git shows {what}. The done-when allows only '
                            f"the request's line, at the end of README.md. {STEP} {rule}")

    if problems:
        print(f"Not yet: {len(problems)} left.")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    print("Done: each mode of Codex is an agent, and your answer matches what Git shows.")


if __name__ == "__main__":
    main()
