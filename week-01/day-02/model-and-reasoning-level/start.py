"""Build this exercise's starting repository, lab/. Run it through the reset command:
python3 ~/practice/reset.py model-and-reasoning-level

lab/ is the week's lab repository after its run 2, as the course team committed it. It holds the
simulated notes, the field list, the route to the model, the lab's agent configuration and the
data-rules check. It also holds the output schema, and the extractor with its tests. Then the course
team commits three files in docs/, from files/. The first holds the scores of two models on the same
20 notes. The second holds the next two tasks for the coding agent, and the command that sets the level of
each agent. The third is the description of the next pull request, with the table that the learner fills in.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import TEAM, build  # noqa: E402

REPO = HERE / "lab"
FILES = ["docs/model-scores.md", "docs/next-tasks.md", "docs/pull-request.md"]


def git(*args):
    subprocess.run(["git", *TEAM, *args], cwd=REPO, check=True, capture_output=True)


build(REPO, "run2")
for path in FILES:
    shutil.copy(HERE / "files" / pathlib.Path(path).name, REPO / path)
git("add", *FILES)
git("commit", "-q", "-m", "Add the facts and the description for the next pull request")
