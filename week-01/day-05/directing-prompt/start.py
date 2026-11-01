"""Build this exercise's starting repository, lab/. Run it through the reset command:
python3 ~/practice/reset.py directing-prompt

lab/ is the week's lab repository after its run 1, as the course team committed it. It holds the
simulated notes, the field list and the route to the model. It also holds the coding agent's
configuration, the data-rules check, and run 1's output schema and its tests. Run 1's catch-up point
in the week's live build also adds "the tests added to the deny rule", so the course team commits
that next. Then it commits what run 2 starts from: the system prompt and two model replies recorded
earlier, taken from lab-states/run2. Last, start.py puts run2-prompt.txt (files/run2-prompt.txt) at
the top of lab/, with its Goal written. Git does not track that file: start.py lists it in
lab/.git/info/exclude.

check.py calls build_start() to build the same start in a copy, for the course's run 2.
"""
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
STATES = next(p for p in HERE.parents if (p / "lab-states").is_dir()) / "lab-states"
sys.path.insert(0, str(STATES))
from build_lab import TEAM, build  # noqa: E402

PROMPT = "run2-prompt.txt"
DENY = "Edit(/tests/test_schema.py)"
RUN2_INPUTS = ["prompts/system.txt", "tests/recorded/0147.json", "tests/recorded/0102.json"]


def build_start(lab):
    lab = pathlib.Path(lab)

    def git(*args):
        subprocess.run(["git", *TEAM, *args], cwd=lab, check=True, capture_output=True)

    build(lab, "run1")
    # Run 1's catch-up point: the accepted tests in the deny rule. A later run1 state may hold it already.
    settings = lab / ".claude" / "settings.json"
    config = json.loads(settings.read_text())
    deny = config.setdefault("permissions", {}).setdefault("deny", [])
    if DENY not in deny:
        deny.append(DENY)
        settings.write_text(json.dumps(config, indent=2) + "\n")
        git("add", ".claude/settings.json")
        git("commit", "-q", "-m", "Deny the coding agent edits to the accepted run 1 tests")
    for path in RUN2_INPUTS:
        (lab / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(STATES / "run2" / path, lab / path)
    git("add", *RUN2_INPUTS)
    git("commit", "-q", "-m", "Add the system prompt and two model replies recorded for run 2's tests")
    shutil.copy(HERE / "files" / PROMPT, lab / PROMPT)
    (lab / ".git" / "info").mkdir(exist_ok=True)
    with open(lab / ".git" / "info" / "exclude", "a") as exclude:
        exclude.write(PROMPT + "\n")


if __name__ == "__main__":
    build_start(HERE / "lab")
