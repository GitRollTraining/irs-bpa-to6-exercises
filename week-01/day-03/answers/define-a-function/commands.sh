# The answer to "Define one function, and test both cases".
# Run it from ~/practice/week-01/day-03/define-a-function/lab, after python3 ~/practice/reset.py define-a-function:
#   sh ../../answers/define-a-function/commands.sh
# It puts the fixed function list in place, and the two replies that the course kept for it. So ask.py
# sends no question to the model: it shows the kept replies. Then the check prints Done:.
# A stand-in claude that fails comes first on PATH for ask.py. If the kept replies do not match the list,
# ask.py stops there. So this file never calls the model.
# decisions.md gives the rule for each change, and the other answers that the check accepts.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"
STOP="$(mktemp -d)"
trap 'rm -rf "$STOP"' EXIT
printf '#!/bin/sh\necho "commands.sh calls no model: the kept replies do not match the function list." >&2\nexit 1\n' > "$STOP/claude"
chmod +x "$STOP/claude"

cp "$ANSWER/functions.json" functions.json
mkdir -p replies
cp -R "$ANSWER/replies/." replies/
PATH="$STOP:$PATH" python3 ask.py
python3 ../check.py
