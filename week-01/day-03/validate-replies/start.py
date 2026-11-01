"""Build this exercise's starting repository, lab/. Run it through the reset command:
`python3 ~/practice/reset.py validate-replies`

lab/ is the week's lab repository after its run 2, as the course team committed it. It holds the
simulated notes and the field list. It holds the route to the model, the agent's configuration and
the data-rules check. It holds the output schema, and the extractor with its tests. On main, the
course team then adds eight replies (files/replies/) and count_failures.py, which gives each reply
to check_reply. Replies 0102 and 0147 are the lab's recorded replies, from tests/recorded/. The
other six are hand-written, each to show a failure. On the branch fewer-failures, checked out, a
teammate then commits a change to the schema and to check_reply (files/teammate/). The learner
fixes that change.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import TEAM, build  # noqa: E402

REPO = HERE / "lab"
FILES = HERE / "files"
TEAMMATE = ["-c", "user.name=Teammate", "-c", "user.email=teammate@example.invalid"]


def git(who, *args):
    subprocess.run(["git", *who, *args], cwd=REPO, check=True, capture_output=True)


build(REPO, "run2")
shutil.copytree(FILES / "replies", REPO / "replies")
shutil.copy(FILES / "count_failures.py", REPO / "count_failures.py")
git(TEAM, "add", "replies", "count_failures.py")
git(TEAM, "commit", "-q", "-m", "Add eight replies, two recorded and six hand-written, and count_failures.py")
git(TEAM, "switch", "-q", "-c", "fewer-failures")
shutil.copytree(FILES / "teammate", REPO, dirs_exist_ok=True)
git(TEAMMATE, "add", "schema/output.schema.json", "extractor.py")
git(TEAMMATE, "commit", "-q", "-F", str(FILES / "teammate-commit.txt"))
