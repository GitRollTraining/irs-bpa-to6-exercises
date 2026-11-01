"""Build this exercise's starting state. Run it through the reset command:
python3 ~/practice/reset.py push-after-rejection

shared.git/ is the lab's remote. It takes the place of a repository on a Git host. It holds the week's
lab at its saved state run2, and one more commit of the course team: docs/remote.md, which names the
lab's remote (files/remote.md). extractor/ is your clone of it, with your commit on top: a test that a
coding agent wrote, which you read and accepted (files/agent-test.txt). After your clone, a
teammate pushes one commit to shared.git (files/teammate-check.txt, files/teammate-test.txt).
mirror.git/ is a second repository, empty. Last, this script sets three things in your clone: an
editor that closes at once, no origin/HEAD, and the push URL of origin, to mirror.git/. In the
scenario, the coding agent set that push URL. The course made up every file.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import TEAM, build  # noqa: E402

CLONE = HERE / "extractor"
SHARED = HERE / "shared.git"
MIRROR = HERE / "mirror.git"
FILES = HERE / "files"
TEAMMATE = ["-c", "user.name=Teammate", "-c", "user.email=teammate@example.invalid"]
# The check finds the teammate's commit by this name in shared.git. A fetch does not copy it.
TEAMMATE_REF = "refs/course/teammate"


def git(*args, cwd=None):
    done = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return done.stdout.strip()


def empty(folder):
    """Empty a folder in place, so that a terminal open inside it keeps working."""
    folder.mkdir(exist_ok=True)
    for child in folder.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def configured(key):
    return subprocess.run(["git", "config", key], cwd=CLONE, capture_output=True, text=True).stdout.strip()


for folder in (CLONE, SHARED, MIRROR):
    empty(folder)
git("init", "-q", "--bare", "-b", "main", str(SHARED))
git("init", "-q", "--bare", "-b", "main", str(MIRROR))

with tempfile.TemporaryDirectory() as temp:
    # The team's work, pushed to shared.git, and your clone of it.
    team = pathlib.Path(temp) / "lab"
    build(team, "run2")
    shutil.copy(FILES / "remote.md", team / "docs" / "remote.md")
    git(*TEAM, "add", "docs/remote.md", cwd=team)
    git(*TEAM, "commit", "-q", "-m", "Name the lab's remote", cwd=team)
    git("push", "-q", str(SHARED), "main", cwd=team)
    git("clone", "-q", str(SHARED), str(CLONE))

    # The teammate's commit, pushed after your clone: a check of the form field, and its test.
    source = (team / "extractor.py").read_text()
    anchor = "    return fields\n"
    if source.count(anchor) != 1:
        sys.exit("start.py: extractor.py in lab-states/run2 changed. Put the teammate's check in by hand.")
    (team / "extractor.py").write_text(source.replace(anchor, (FILES / "teammate-check.txt").read_text() + anchor))
    shutil.copy(FILES / "teammate-test.txt", team / "tests" / "test_own_checks.py")
    git(*TEAMMATE, "add", "extractor.py", "tests/test_own_checks.py", cwd=team)
    git(*TEAMMATE, "commit", "-q", "-F", str(FILES / "teammate-commit.txt"), cwd=team)
    git("push", "-q", str(SHARED), "main", cwd=team)
    git("--git-dir", str(SHARED), "update-ref", TEAMMATE_REF, git("rev-parse", "HEAD", cwd=team))

# Your commit: the coding agent's test, which you read and accepted. This script makes it with your
# Git name and email, or with a stand-in name where Git has none yet.
with open(CLONE / "tests" / "test_extractor.py", "a") as tests:
    tests.write((FILES / "agent-test.txt").read_text())
you = [] if configured("user.name") and configured("user.email") else \
    ["-c", "user.name=You", "-c", "user.email=you@example.invalid"]
git("add", "tests/test_extractor.py", cwd=CLONE)
git(*you, "commit", "-q", "-F", str(FILES / "your-commit.txt"), cwd=CLONE)

# No Git command in your clone waits in an editor: a notebook cell cannot answer one. A merge
# keeps the message that Git writes, as --no-edit does.
git("config", "core.editor", "true", cwd=CLONE)
# Your clone keeps no origin/HEAD, so that Git's output names only what section 4.2 teaches.
git("remote", "set-head", "origin", "--delete", cwd=CLONE)
git("config", "remote.origin.followRemoteHEAD", "never", cwd=CLONE)
# Where origin pushes, as the coding agent of the scenario set it: the learner reads it with git remote -v.
git("remote", "set-url", "--push", "origin", str(MIRROR), cwd=CLONE)
