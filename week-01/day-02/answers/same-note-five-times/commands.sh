# The answer to "Send two notes five times each, and record what the note does not state".
# Run it from ~/practice/week-01/day-02/same-note-five-times/lab, after python3 ~/practice/reset.py same-note-five-times:
#   sh ../../answers/same-note-five-times/commands.sh
# It calls no model. It puts the ten replies of the run of 2026-10-20 in the folder where send_five.py
# saves the replies to prompt.txt. Then it writes the record for them and runs the check, which prints Done:.
# It replaces your replies and your record, so it stops if you changed record.md or sent a reply.
set -e
ANSWER="$(cd "$(dirname "$0")" && pwd)"

# The replies, as the model gave them on 2026-10-20, in the folder for the prompt in prompt.txt.
FOLDER="$(python3 -c 'import pathlib, send_five; print(send_five.reply_folder(pathlib.Path(".")).as_posix())')"
if [ -n "$(ls -A "$FOLDER" 2>/dev/null)" ] || ! git diff --quiet -- record.md; then
  echo "commands.sh stops here, and keeps your replies and your record."
  echo "To see the answer in lab/, run python3 ~/practice/reset.py same-note-five-times first. Then run commands.sh again."
  exit 1
fi
mkdir -p "$FOLDER"
cp "$ANSWER"/replies/*.txt "$FOLDER"/
python3 send_five.py 0147 0104 > /dev/null  # It sends nothing, and writes field-by-field.txt.

# The record: in each row, the replies whose value the note does not state.
cp "$ANSWER/record.md" record.md

python3 ../check.py
