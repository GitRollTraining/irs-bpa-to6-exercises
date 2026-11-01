# The answer to "Score the prompt on a labelled set, and revise it once".
# Run it from ~/practice/week-01/day-03/score-the-prompt/extractor, after python3 ~/practice/reset.py score-the-prompt:
#   sh ../../answers/score-the-prompt/commands.sh
# It makes no model call. In place of the 20 calls of the second score, it copies the kept run of the
# answer's prompt, run/. The last command is the check, which prints Done:.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

cp "$ANSWER/failure.md" evaluation/failure.md     # One wrong value of the first score, and its cause.
cp "$ANSWER/system.txt" prompts/system.txt        # The change. Each example gives the form number only.
mkdir -p evaluation/runs/2
cp "$ANSWER"/run/* evaluation/runs/2/             # The kept run of this prompt.
python3 evaluation/score.py                       # The second score. It finds the kept run, and sends nothing.
git add prompts/system.txt evaluation
git commit -q -m "Revise the prompt once"
python3 ../check.py
