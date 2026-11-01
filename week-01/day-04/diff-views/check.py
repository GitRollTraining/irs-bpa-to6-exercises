"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads, through Git, the commits that you made after the commit of the course team that added
docs/directing-prompt.md. It looks for the change that the directing prompt asks for, and for any
file that the directing prompt does not allow. It also reads the staging area, to name a staged file
that the directing prompt does not allow. When a commit holds the change to extractor.py, it also
runs the tests on a copy of your last commit. It starts no agent, calls no model and needs no
network: a stand-in claude that always fails is first on the PATH of the tests.
"""
import io
import os
import pathlib
import re
import subprocess
import sys
import tarfile
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE / "lab"
START = "before-run"  # the course team's last commit, before the agent's run
TESTS = "tests/test_extractor.py"
ASKED = ("extractor.py", TESTS)  # the files that the directing prompt allows
RESET = "python3 ~/practice/reset.py diff-views"
# Each message names the row of the table in step 2 that gives the answer, and the line of section 4.3.
ROW2_LINE = ("Section 4.3, under \"Start wide, then point --exit-code at HEAD for the tests.\": \"a file outside what "
             "the directing prompt allowed is a finding\".")
ROW3_LINE = "Section 4.3, the list \"The trap: the plain form\": \"Run git diff --staged before every commit\"."
STAGED = f"Row 3 of the table in step 2 gives the answer. {ROW3_LINE}"
BY_HAND = f"The steps change no file by hand. {STAGED} To start again, run {RESET}."
# After the reset, prompts/system.txt and the test are staged again, and extractor.py is not.
WAY_BACK = ("Then take prompts/system.txt out of the staging area, and stage extractor.py, before you commit. Rows 2 "
            f"and 3 of the table in step 2 give the answer. {ROW2_LINE} {ROW3_LINE}")


def git(*args):
    return subprocess.run(["git", "-c", "color.ui=false", *args], cwd=REPO, capture_output=True, text=True)


def stop(message):
    print("Not yet: " + message)
    sys.exit(1)


def blob(rev, path):
    found = git("show", f"{rev}:{path}")
    return found.stdout if found.returncode == 0 else None


def on_disk(path):
    return (REPO / path).read_text() if (REPO / path).is_file() else None


def test_names(text):
    return set(re.findall(r"^def (test_\w+)", text or "", re.M))


def pytest_on(rev):
    """The last line of pytest, and its return code, on a copy of the commit rev."""
    archive = subprocess.run(["git", "archive", "--format=tar", rev], cwd=REPO, capture_output=True)
    with tempfile.TemporaryDirectory() as tmp:
        copy, bin_dir = pathlib.Path(tmp) / "copy", pathlib.Path(tmp) / "bin"
        copy.mkdir()
        bin_dir.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            try:
                tar.extractall(copy, filter="data")
            except TypeError:  # a Python without extraction filters
                tar.extractall(copy)
        claude = bin_dir / "claude"
        claude.write_text("#!/bin/sh\necho 'claude is off during the done check' >&2\nexit 1\n")
        claude.chmod(0o755)
        # PY_COLORS=0: a notebook's kernel sets FORCE_COLOR, and colored output hides pytest's last line.
        env = {**os.environ, "PY_COLORS": "0", "PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", "")}
        run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=copy,
                             capture_output=True, text=True, timeout=300, env=env)
    lines = (run.stdout.strip() or run.stderr.strip() or "no output").splitlines()
    return run.returncode, re.sub(r" in [\d.]+s$", "", lines[-1].strip())  # no time, so each run prints the same


if not (REPO / ".git").is_dir() or git("rev-parse", "-q", "--verify", f"refs/tags/{START}").returncode:
    stop(f"the folder lab does not hold the repository of this exercise. Run {RESET}.")
if git("merge-base", "--is-ancestor", START, "HEAD").returncode:
    stop("your history no longer holds the commit of the course team that added docs/directing-prompt.md. "
         f"To start again, run {RESET}.")

problems = []
log = git("log", "--no-renames", "--format=", "--name-only", f"{START}..HEAD")
in_commits = {line for line in log.stdout.splitlines() if line.strip()}
outside = sorted(in_commits - set(ASKED))
if outside:
    # The reset undoes every commit and stages prompts/system.txt and the test again, so this line alone gives the
    # whole way back.
    problems.append(f"a commit holds {', '.join(outside)}, but docs/directing-prompt.md says \"Change no other file\". "
                    f"That change must stay out of your commits. To start again, run {RESET}. {WAY_BACK}")

has_change = blob("HEAD", "extractor.py") != blob(START, "extractor.py")
gone = False  # True when only the reset can bring back the agent's change to extractor.py
if not has_change and not outside:
    staged = git("diff", "--cached", "--no-renames", "--name-only").stdout.splitlines()
    if "extractor.py" not in staged and on_disk("extractor.py") == blob(START, "extractor.py"):
        # Neither the staging area nor the disk holds the agent's change, such as after git restore extractor.py.
        # The reset brings back the agent's test too, so this line gives the whole way back.
        gone = True
        problems.append("no commit holds the change to extractor.py that docs/directing-prompt.md asks for, and "
                        "extractor.py is as it was before the agent's run. To get the agent's change back, run "
                        f"{RESET}. {WAY_BACK}")
    else:
        # The moves come from what the staging area holds now: a file to take out is staged and not allowed.
        take_out = sorted(set(staged) - set(ASKED))
        if "extractor.py" in staged:
            why, moves = "The staging area holds it, but no commit does yet.", []
        else:
            why, moves = "The agent did not stage it, so a commit leaves it out.", ["Stage extractor.py."]
        rows = STAGED
        if take_out:
            moves.insert(0, f"docs/directing-prompt.md says \"Change no other file\", so take {', '.join(take_out)} "
                            "out of the staging area.")
            rows = f"Rows 2 and 3 of the table in step 2 give the answer. {ROW2_LINE} {ROW3_LINE}"
        moves.append("Then commit." if moves else "Commit.")
        problems.append("no commit holds the change to extractor.py that docs/directing-prompt.md asks for. "
                        f"{why} {' '.join(moves)} {rows}")
before, now = test_names(blob(START, TESTS)), test_names(blob("HEAD", TESTS))
if not now - before and not outside and not gone:
    if not test_names(blob("", TESTS)) - before and not test_names(on_disk(TESTS)) - before:
        # Neither the staging area nor the disk holds the agent's new test.
        problems.append(f"no commit adds the test to {TESTS} that docs/directing-prompt.md asks for, and neither the "
                        f"staging area nor the disk holds it. To get the agent's change back, run {RESET}. {WAY_BACK}")
    else:
        problems.append(f"no commit adds the test to {TESTS} that docs/directing-prompt.md asks for. The agent staged "
                        f"it. Keep it staged, or stage it again, then commit. {STAGED}")
if before - now:
    problems.append(f"your commits remove a test from {TESTS}: {', '.join(sorted(before - now))}. {BY_HAND}")

# Without the change to extractor.py, the agent's new test fails: that is the missing change, not a second fault.
if has_change:
    code, last = pytest_on("HEAD")
    if code != 0:
        problems.append(f"the tests fail on your last commit. The last line from pytest is: {last}. {BY_HAND}")

if problems:
    print(f"Not yet: {len(problems)} left.")
    print("\n".join(f"- {problem}" for problem in problems))
    sys.exit(1)
print("Done: your commits hold the change that the directing prompt asks for, and the tests pass on your last "
      "commit. No commit holds a file that the directing prompt does not allow.")
