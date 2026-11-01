# Exercise: Write the directing prompt for run 2

After this exercise, you can write the directing prompt for run 2, with a done-when that anyone can check from a command.

**Scenario:** Run 1 added the output schema and its tests. Run 2 asks a coding agent for the extractor.

**Success criterion:** from `lab`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-05/directing-prompt/lab`, in VS Code. In the Explorer: week-01 › day-05 › directing-prompt › lab. Each path in this exercise starts there. Do not use AI tools.

**Start from:** the lab after run 1. Run `python3 ~/practice/reset.py directing-prompt`. It prints `directing-prompt is back as it was supplied.` Then run `cd ~/practice/week-01/day-05/directing-prompt/lab`. To start again, run the same reset. It removes your text.

**What you have:** `run2-prompt.txt`: the Goal and three empty parts. `../check.py`, the check. Rules: the Opening and section 5.1, "A directing prompt with a done-when".

## Steps

1. Run `git log --oneline --name-only -3`. You should see run 1's files, Claude Code's settings, and the files added for run 2.
2. Open `run2-prompt.txt`. After each empty label, write its line from this table. Do not change the Goal.

| Part | Write this | Why |
|---|---|---|
| Context | read model.py, prompts/system.txt and schema/output.schema.json. The tests use the replies in tests/recorded/. | The function sends prompts/system.txt through model.py to the model. It checks each reply against schema/output.schema.json. The tests use the recorded replies. Without these paths, the agent guesses. Section 5.1, under "A one-line task is a wish": "Reference specific files". |
| Constraints | The tests call no model. Do not edit anything outside extractor.py and tests/test_extractor.py. Do not log note text. | The Goal's function calls the model, whose reply can change. So its tests use the recorded replies. If the agent changes run 1's files or the recorded replies, wrong code can pass. So it edits only the Goal's two files. A log line with note text copies taxpayer data. Section 5.1, run 1's table, Constraints: "Do not call any model. Do not edit anything outside schema/ and tests/. Do not log note text." The Opening, under "Today's runs build the extractor": "tested on model replies recorded earlier". |
| Done-when | pytest tests/test_extractor.py passes. It includes one reply that must fail (amount_in_question missing) and note 0102, for which the function must return amount_in_question null. | Anyone can run the command. A reply that must fail catches an extractor that accepts any reply. Note 0102 has a recorded reply and names no amount. So its test catches an extractor that supplies an amount. Section 5.1, under "Only the done-when": "the part someone who did not watch can check from a command". Run 1's table, Done-when: "it includes one output that must fail (amount_in_question missing)". The Opening, under "Today's runs build the extractor": "A note with no amount: amount_in_question is null". |

3. Save the file. Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then do this step again.

**Answer:** `~/practice/week-01/day-05/answers/directing-prompt/` holds the finished prompt, `decisions.md`, and `commands.sh`, which ends with `Done:`.

## Afterwards, together

- When would a run change run 1's schema, and what would its Constraints say?
- Which wrong run 2 would still pass your done-when, and why?
- In your own work, what command would show that a change works?
