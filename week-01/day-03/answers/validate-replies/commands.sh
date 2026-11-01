# The answer to "Check replies against a schema and your own check". Run it from
# `~/practice/week-01/day-03/validate-replies/lab`, after `python3 ~/practice/reset.py validate-replies`:
#   `sh ../../answers/validate-replies/commands.sh`
# As the steps of the exercise do, it makes the three changes of the table in step 2. Then it counts
# the failures again, and runs the check, which prints Done:. decisions.md gives the reason for each
# change, and the other answers that the check accepts.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

# 1. Only the amount may be null: line 10 makes next_action a string again.
cp "$ANSWER/schema/output.schema.json" schema/output.schema.json
# 2 and 3. The six lines from "# The model sometimes" are gone. import datetime, and your own check just above return fields.
cp "$ANSWER/extractor.py" extractor.py
python3 count_failures.py
python3 ../check.py
