"""Build this exercise's starting repository, extractor/. Run it through the reset command:
python3 ~/practice/reset.py commit-three-of-four

extractor/ is the week's lab repository after its run 2, as the course team committed it. On top of
it, not committed, are a coding agent's changes to four files (files/agent-run.patch), and the log
directory that its run wrote (files/logs/). The learner asked for three of the changes
(agent-session.txt). The fourth change is a debugging print in model.py. It writes the whole note to
logs/extractor.log. Last, this script writes .git/info/agent-run.json for check.py. That file holds the
Git id of each of the four files, as the course committed it and as the agent left it.
"""
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
from build_lab import build  # noqa: E402

REPO = HERE / "extractor"
PATCH = HERE / "files" / "agent-run.patch"
CHANGED = ("extractor.py", "tests/test_extractor.py", "README.md", "model.py")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


build(REPO, "run2")
course = {path: git("rev-parse", f"HEAD:{path}").stdout.strip() for path in CHANGED}
applied = git("apply", str(PATCH))
if applied.returncode != 0:
    # The patch applies to the lab at run 2. A change to one of these four files in the kit can stop it.
    sys.exit("start.py: the changes of the agent do not apply to the lab at run 2. Tell your trainer.\n"
             "For the course team: make files/agent-run.patch again on the lab's new files.\n" + applied.stderr)
shutil.copytree(HERE / "files" / "logs", REPO / "logs")
agent = {path: git("hash-object", "--", path).stdout.strip() for path in CHANGED}
record = REPO / ".git" / "info" / "agent-run.json"
record.parent.mkdir(exist_ok=True)
record.write_text(json.dumps({"course": course, "agent": agent}, indent=1) + "\n")
