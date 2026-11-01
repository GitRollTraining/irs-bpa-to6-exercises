"""Build this exercise's starting repository, extractor/. Run it through the reset command:
python3 ~/practice/reset.py tool-modes

extractor/ is the week's lab repository at its saved state configured. The course team made its
three commits. The first adds the simulated notes, the field list and the route to the model. The
second adds the coding agent's configuration. The third records the data-rules check, passed, before
any AI tool. That configuration is .claude/settings.json, the settings file of Claude Code. Codex
does not use it. The lab has no settings file for Codex.

Then this script puts modes.md, the learner's table (files/modes.md), in extractor/. Git does not
track the table: extractor/.git/info/exclude lists it. Last, the script keeps the start commit in
extractor/.git/info/exercise-start, so that ../check.py finds each change after the start, also a
change that someone committed.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import build  # noqa: E402

REPO = HERE / "extractor"

build(REPO, "configured")
shutil.copy(HERE / "files" / "modes.md", REPO / "modes.md")
info = REPO / ".git" / "info"
info.mkdir(exist_ok=True)
with open(info / "exclude", "a") as exclude:
    exclude.write("modes.md\n")
start = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True, capture_output=True, text=True)
(info / "exercise-start").write_text(start.stdout)
