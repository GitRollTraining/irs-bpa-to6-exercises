"""Build this exercise's starting repository, lab/. Run it through the reset command:
python3 ~/practice/reset.py diff-views

lab/ is the week's lab repository at its saved state run2, as the course team committed it. Then the
course team commits docs/directing-prompt.md (files/directing-prompt.md): the directing prompt of
one more run of the coding agent, and the agent's report. That commit has the tag before-run, which
check.py reads. Last comes the agent's run (files/agent-run.patch), not committed: it changes
extractor.py, tests/test_extractor.py and prompts/system.txt, and the agent staged the last two.
The directing prompt allows only the first two. The course made up everything in lab/.
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


def git(*args):
    subprocess.run(["git", *args], cwd=REPO, check=True, capture_output=True)


build(REPO, "run2")
shutil.copy(FILES / "directing-prompt.md", REPO / "docs" / "directing-prompt.md")
git(*TEAM, "add", "docs/directing-prompt.md")
git(*TEAM, "commit", "-q", "-m", "Add the directing prompt for one more run of the coding agent")
git(*TEAM, "tag", "before-run")
git("apply", str(FILES / "agent-run.patch"))
git("add", "tests/test_extractor.py", "prompts/system.txt")
