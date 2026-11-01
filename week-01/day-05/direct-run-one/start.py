"""Build this exercise's starting repository, lab/. Run it through the reset command:
python3 ~/practice/reset.py direct-run-one

lab/ is the week's lab repository at its saved state "configured". It holds the simulated notes,
the field list, the route to the model, the coding agent's configuration and the data-rules check.
The course team committed them, and no AI tool touched them. Then the course adds two files. It
lists them in lab/.git/info/exclude, so the lab's commits leave them out. run1-prompt.txt holds the
directing prompt of run 1, from the table in section 5.1. run-1-record.md is your report on the run.
The list also holds tests.diff, which cell 2 of the notebook writes: the test files' diff, for the
editor. So Git leaves it out of each commit and of git status too.
"""
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import build  # noqa: E402

LAB = HERE / "lab"
LEFT_OUT = ("run1-prompt.txt", "run-1-record.md")
EXCLUDED = LEFT_OUT + ("tests.diff",)

build(LAB, "configured")
for name in LEFT_OUT:
    shutil.copy(HERE / "files" / name, LAB / name)
with open(LAB / ".git" / "info" / "exclude", "a") as exclude:
    exclude.write("".join(name + "\n" for name in EXCLUDED))
