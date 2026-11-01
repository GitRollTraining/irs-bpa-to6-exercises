# The answer to "Choose a model and two levels, and record why". Run it from
# ~/practice/week-01/day-02/model-and-reasoning-level/lab, after python3 ~/practice/reset.py model-and-reasoning-level:
#   sh ../../answers/model-and-reasoning-level/commands.sh
# As the exercise's steps do, it fills in the table, commits it, and runs the check, which prints Done:.
# decisions.md gives the rule for each choice, and the other answers that the check accepts.
# The exercise calls no model and starts no coding agent, so this answer keeps no replies.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

cp "$ANSWER/pull-request.md" docs/pull-request.md
git add docs/pull-request.md
git commit -q -m "Choose the model and levels"
git log --oneline --no-decorate -1   # your commit, above the commits of the course team

python3 ../check.py
