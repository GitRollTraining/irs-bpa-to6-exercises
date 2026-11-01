# The answer to "Check the remote, push, get rejected, and push again".
# Run it from ~/practice/week-01/day-04/push-after-rejection/extractor, after
# python3 ~/practice/reset.py push-after-rejection:
#   sh ../../answers/push-after-rejection/commands.sh
# It runs the commands of the steps in order. Then it runs the check, which prints Done:.
# decisions.md gives each answer, its reason, and what else the check accepts.
set -e

# Step 1: your commit, with one file changed: tests/test_extractor.py.
git show --stat HEAD

# Step 2. Check the remote: the (fetch) line names shared.git, the (push) line mirror.git.
git remote -v
# Set the push line.
git remote set-url --push origin ~/practice/week-01/day-04/push-after-rejection/shared.git
git remote -v
# Push: the lab's remote rejects it, as your teammate pushed first.
if git push; then echo "Not expected: the push was not rejected."; exit 1; fi
# Fetch, read what came in, merge, and push again.
git fetch
git show --stat origin/main
git merge --no-edit origin/main
git push

# Step 3.
python3 ../check.py
