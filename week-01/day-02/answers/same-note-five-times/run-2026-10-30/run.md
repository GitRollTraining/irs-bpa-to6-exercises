# The run of 2026-10-30

On 2026-10-30, the course team did this exercise in the notebook. Cell 2 sent each note five times, with `prompt.txt` and no schema. `replies/` holds the ten replies, as `model.py` gave them. `record.md` is the record for these replies. The check accepts it.

- Route: `claude-code`, in `model-route.json`. `model.py` runs `claude -p`.
- Version of `claude`: 2.1.314.
- Model: `haiku`, in `model-route.json`. `model.py` gives no model name. One more call from a terminal, 4 minutes later, with the same `claude` and flags, used `claude-haiku-5-5` for `haiku`.
- Calls: 10 in the notebook. One more call from a terminal asked again for reply 5 to note 0104. `terminal/0104-5.txt` holds that reply. It gives null.
- Date: 2026-10-30.
- Place: a computer of the course team, not the workspace where you work.

To see this run in `lab`, run the reset first. Then, from `lab`, run `sh ../../answers/same-note-five-times/run-2026-10-30/commands.sh`. It calls no model. It puts the ten replies and this record in `lab`, and the check prints `Done:`.
