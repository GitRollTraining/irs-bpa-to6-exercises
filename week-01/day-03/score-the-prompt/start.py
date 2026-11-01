"""Build this exercise's starting repository, extractor/. Run it through the reset command:
python3 ~/practice/reset.py score-the-prompt

extractor/ is the week's lab repository at its saved state run2, as the course team committed it. It
holds the simulated notes, the field list, the route to the model and the agent's configuration. It
also holds the data-rules check, the output schema, and the extractor with its tests. Then come three
commits:

1. The course team starts the evaluation set (files/evaluation/): 20 labelled notes, the scorer and
   the write-up for one failure.
2. A teammate changes prompts/system.txt (files/teammate-system.txt).
3. The course team saves a first run of the set on that prompt in evaluation/runs/1/, with its
   score. The tag first-score marks this commit.

The replies in files/first-run/ are the model's replies, as model.py returned them. The course team
ran the teammate's prompt once on 2026-10-30, outside the hosted workspace: route claude-code, model
haiku, Claude Code 2.1.314. FIRST_RUN is the record of that run.
"""
import json
import pathlib
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"))
sys.path.insert(0, str(HERE / "files" / "evaluation"))
from build_lab import TEAM, build  # noqa: E402
from score import fingerprint  # noqa: E402

REPO = HERE / "extractor"
FILES = HERE / "files"
TEAMMATE = ["-c", "user.name=Teammate", "-c", "user.email=teammate@example.invalid"]
FIRST_RUN = {"model": "haiku", "route": "claude-code", "date": "2026-10-30",
             "replies": "From the model, through model.py, outside the hosted workspace."}


def git(who, *args):
    subprocess.run(["git", *who, *args], cwd=REPO, check=True, capture_output=True)


build(REPO, "run2")
shutil.copytree(FILES / "evaluation", REPO / "evaluation", dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__"))
git(TEAM, "add", "evaluation")
git(TEAM, "commit", "-q", "-m", "Start the evaluation set: 20 labelled notes, the scorer and a write-up")

shutil.copy(FILES / "teammate-system.txt", REPO / "prompts" / "system.txt")
git(TEAMMATE, "add", "prompts/system.txt")
git(TEAMMATE, "commit", "-q", "-m", "Revise the system prompt: five replies read, and all look right")

first = REPO / "evaluation" / "runs" / "1"
first.mkdir(parents=True)
for reply in sorted((FILES / "first-run").glob("*.txt")):
    shutil.copy(reply, first / reply.name)
prompt = (REPO / "prompts" / "system.txt").read_text()
shutil.copy(REPO / "prompts" / "system.txt", first / "prompt.txt")
code = fingerprint(prompt, (REPO / "schema" / "output.schema.json").read_text())
(first / "run.json").write_text(json.dumps({"fingerprint": code, **FIRST_RUN}, indent=2) + "\n")
subprocess.run([sys.executable, "evaluation/score.py", "--first"], cwd=REPO, check=True, capture_output=True)
git(TEAM, "add", "evaluation/runs")
git(TEAM, "commit", "-q", "-m", "Save the first run of the set on the teammate's prompt, with its score")
git(TEAM, "tag", "first-score")
