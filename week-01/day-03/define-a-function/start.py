"""Build this exercise's starting repository, lab/. Run it through the reset command:
python3 ~/practice/reset.py define-a-function

lab/ is the week's lab repository at its saved state configured, after the data-rules check, as the course team
committed it. It holds the simulated notes, the field list, the coding agent's configuration, the data-rules check
and model.py, which sends a question to the model. Then a teammate commits a helper for questions to the model
(files/): the function list functions.json, tools.py, ask.py and system-prompt.txt.
ask.py saves the model's replies in replies/, which the repository's commits leave out.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import build  # noqa: E402

REPO = HERE / "lab"
TEAMMATE = ["-c", "user.name=Teammate", "-c", "user.email=teammate@example.invalid"]
HELPER = ["functions.json", "tools.py", "ask.py", "system-prompt.txt"]


def git(*args):
    subprocess.run(["git", *TEAMMATE, *args], cwd=REPO, check=True, capture_output=True)


build(REPO, "configured")
for name in HELPER:
    shutil.copy(HERE / "files" / name, REPO / name)
git("add", *HELPER)
git("commit", "-q", "-F", str(HERE / "files" / "teammate-commit.txt"))
with open(REPO / ".git" / "info" / "exclude", "a") as exclude:
    exclude.write("replies/\n")
