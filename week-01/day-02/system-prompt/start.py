"""Build this exercise's starting repository, lab/. Run it through the reset command:
python3 ~/practice/reset.py system-prompt

lab/ is the week's lab repository at its saved state run1. It holds the simulated notes, the field
list and the route to the model. It also holds the agent's configuration, the data-rules check, and the
output schema with its tests. Then the course team commits the first part of run 2: the extractor and
its tests, from lab-states/run2/. A draft system prompt, files/system.txt, takes the place of the prompt
of run 2. The folder tests/recorded/ is empty, so the tests that read it fail. ../record.py keeps each
run's replies in runs/, which lab/.git/info/exclude keeps out of every commit.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
STATES = next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"
sys.path.insert(0, str(STATES))
from build_lab import TEAM, build  # noqa: E402

REPO = HERE / "lab"


def git(*args):
    subprocess.run(["git", *TEAM, *args], cwd=REPO, check=True, capture_output=True)


def place(source, target):
    (REPO / target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source, REPO / target)


build(REPO, "run1")
place(STATES / "run2" / "extractor.py", "extractor.py")
place(STATES / "run2" / "tests" / "test_extractor.py", "tests/test_extractor.py")
place(HERE / "files" / "system.txt", "prompts/system.txt")
git("add", "extractor.py", "tests/test_extractor.py", "prompts/system.txt")
git("commit", "-q", "-m", "Run 2, first part: add the extractor, its tests and a draft system prompt")
# An empty folder: a commit of tests/recorded/ before the first record then commits nothing, with no error.
(REPO / "tests" / "recorded").mkdir(exist_ok=True)
with open(REPO / ".git" / "info" / "exclude", "a") as exclude:
    exclude.write("runs/\n")
