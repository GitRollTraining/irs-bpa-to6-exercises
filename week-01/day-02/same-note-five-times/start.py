"""Build this exercise's starting repository, lab/. Run it through the reset command:
python3 ~/practice/reset.py same-note-five-times

lab/ is the week's lab repository at its saved state configured. It holds the simulated notes, the
field list, the route to the model, the coding agent's configuration and the data-rules check,
passed. On top, the course team commits three files. prompt.txt is the short prompt of the run of
2026-10-20. send_five.py sends each note five times, and saves each reply. record.md is the
learner's record, with its rows empty. The replies go in replies/, which .git/info/exclude lists,
so no commit holds them.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import TEAM, build  # noqa: E402

REPO = HERE / "lab"
SUPPLIED = ["prompt.txt", "send_five.py", "record.md"]


def git(*args):
    subprocess.run(["git", *TEAM, *args], cwd=REPO, check=True, capture_output=True)


build(REPO, "configured")
for name in SUPPLIED:
    shutil.copy(HERE / "files" / name, REPO / name)
git("add", *SUPPLIED)
git("commit", "-q", "-m", "Add the short prompt, the script that sends each note five times, and the record")
with open(REPO / ".git" / "info" / "exclude", "a") as exclude:
    exclude.write("replies/\n")
