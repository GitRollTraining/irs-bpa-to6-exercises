# The replies of the course's run

These three files are the replies of the model to the answer's prompt, `../system.txt`. The course team ran the cells of the day's notebook on 2026-10-30, with the answer's prompt in `prompts/system.txt`. Cell 3 sent the notes 0147, 0102 and 0104 through the lab's route to the model, `model.py`. Each file holds a reply as `model.py` gave it.

- Route: `claude-code`, as `model-route.json` names it. It runs the command `claude`, version 2.1.314.
- Model: `haiku`, as `model-route.json` names it. This name can point to a newer model with time. The run did not keep the full name of the model.
- Date: 2026-10-30.
- Where: on a computer of the course team, not in the hosted workspace of the course.

Then the course team ran the commands of the exercise's README in a terminal. That run gave the same values for `amount_in_question`: 18400, null and null. Only the words of one `next_action` were different.

`commands.sh` records these replies through `replay.py`, so the check can run with no call to the model.
