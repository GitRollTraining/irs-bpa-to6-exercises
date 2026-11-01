"""Record the kept replies in recorded/ for the prompt as it is now, with no call to the model.

The answer's commands.sh runs it from lab/. It gives ../record.py the kept reply for each note in
place of the lab's route to the model. So the replies go where a run of record.py puts them: into
runs/, and then into tests/recorded/. recorded/README.md says where the kept replies came from.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXERCISE = HERE.parents[1] / "system-prompt"
sys.path.insert(0, str(EXERCISE / "lab"))
sys.path.insert(0, str(EXERCISE))
import model  # noqa: E402  the lab's route to the model, which this script replaces
import record  # noqa: E402


def kept(system_prompt, note_text, schema=None, model=None, functions=None):
    number = re.search(r"Note (\d{4})", note_text).group(1)
    return (HERE / "recorded" / f"{number}.json").read_text()


model.ask = kept
record.main(["0147", "0102", "0104"])
