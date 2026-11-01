# The answer to "Map the modes of the coding tool you use".
# It makes the change of the course's run in Ask for approval, fills in modes.md, and runs the check,
# which prints Done:.
# Run it from ~/practice/week-01/day-04/tool-modes/extractor, after python3 ~/practice/reset.py tool-modes.
# The command:
#   sh ../../answers/tool-modes/commands.sh
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

# The run in Ask for approval. No coding agent runs in this file. git apply makes the change that
# Codex made in the course's run of 2026-10-30: one line at the end of README.md.
# codex-run/README.md tells what Codex did. The run in Read Only changed no file.
git apply "$ANSWER/codex-run/ask-for-approval.diff"

# What Codex changed. HEAD is the form of git diff for all changes since the last commit.
git status --short
git --no-pager diff --no-color HEAD

# modes.md: agent for each mode, and yes for the run in Ask for approval.
# decisions.md gives each answer and its reason.
cp "$ANSWER/modes.md" modes.md
python3 ../check.py
