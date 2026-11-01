# The answer to "Write the directing prompt for run 2". Run it from
# ~/practice/week-01/day-05/directing-prompt/lab, after python3 ~/practice/reset.py directing-prompt:
#   sh ../../answers/directing-prompt/commands.sh
# It writes the course's prompt into run2-prompt.txt, as you write yours in the editor, and runs the
# check, which prints Done:. It commits nothing: Git does not track run2-prompt.txt.
# decisions.md gives the rule for each part, and the other answers that the check accepts.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

cp "$ANSWER/run2-prompt.txt" run2-prompt.txt
cat run2-prompt.txt
python3 ../check.py
