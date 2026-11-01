# The answer to "Write the system prompt, and record three replies".
# Run it from ~/practice/week-01/day-02/system-prompt/lab, after python3 ~/practice/reset.py system-prompt.
# The command is: sh ../../answers/system-prompt/commands.sh
# It writes the answer's prompt, and records the kept replies, with no call to the model.
# Then it runs the tests, commits, and runs the check, which prints Done:.
# decisions.md gives the rule for each change.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

cp "$ANSWER/system.txt" prompts/system.txt
# replay.py gives record.py the kept replies in recorded/, so no call goes to the model. recorded/README.md says where they came from.
python3 "$ANSWER/replay.py"
python3 -m pytest -q --tb=no -p no:cacheprovider
git add prompts/system.txt tests/recorded
git commit -q -m "Write the system prompt"
python3 ../check.py
