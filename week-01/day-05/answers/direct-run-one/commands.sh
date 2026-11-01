# The answer to "Direct the first run and check it yourself".
# Run it from ~/practice/week-01/day-05/direct-run-one/lab, after python3 ~/practice/reset.py direct-run-one:
#   sh ../../answers/direct-run-one/commands.sh
# It starts no coding agent. In place of your agent's run 1, it copies the files of the course's
# Codex run, from agent-run/codex/. agent-run/README.md says what each run of the course is. Then it
# does your part as the steps do, and it runs the check, which prints Done:. decisions.md gives each
# answer and its reason, and what else the check accepts.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

# Step 2. In place of your agent's run 1: the files that the Codex run left.
cp -R "$ANSWER/agent-run/codex/." .

# Run the done-when yourself. Its last line goes into Proof.
python3 -m pytest tests/test_schema.py | tail -n 1

# Stage the run's two folders. Then read the test files' staged diff: here, only its list of files.
git add -- schema tests
git diff --staged --stat -- tests

# Step 3. Your report, as the table gives it. Git leaves run-1-record.md out of the commit.
cp "$ANSWER/run-1-record.md" run-1-record.md
git commit -q -m "Accept run 1"
python3 ../check.py
