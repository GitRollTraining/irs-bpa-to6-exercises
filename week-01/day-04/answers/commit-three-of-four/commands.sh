# The answer to "Commit three changes and leave the fourth out". Run it from
# ~/practice/week-01/day-04/commit-three-of-four/extractor, after python3 ~/practice/reset.py commit-three-of-four:
#   sh ../../answers/commit-three-of-four/commands.sh
# It keeps the log directory out of Git, stages the three changes that you asked for and .gitignore by name,
# commits them, and runs the check, which prints Done:.
# decisions.md gives each answer, its reason and the notebook line.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

# By hand: .gitignore gets the line logs/.
cp "$ANSWER/gitignore.txt" .gitignore
git add extractor.py tests/test_extractor.py README.md .gitignore
# A letter in the first column: staged. The line " M model.py": the debugging print, not staged.
git status --short
git commit -q -m "Log each failed reply by note number"
python3 ../check.py
