# Exercise: Score the prompt on a labelled set, and revise it once

After this exercise, you can score a prompt per field on a labelled set, and revise it on one failure.

**Scenario:** A teammate changed the extractor's prompt. Five replies looked right. Nobody read its score on the set.

**Success criterion:** from `extractor`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-03/score-the-prompt/extractor`, in VS Code. In the Explorer, it is week-01 › day-03 › score-the-prompt › extractor. Each path starts there. `evaluation/score.py` calls the model. Use no other AI tool.

**Start from:** the week's lab, with the teammate's prompt. Run `python3 ~/practice/reset.py score-the-prompt`. It prints `score-the-prompt is back as it was supplied.` Then run `cd ~/practice/week-01/day-03/score-the-prompt/extractor`. To start again, run the same reset. It removes your commits and runs.

**What you have:** `prompts/system.txt`, the teammate's prompt. `evaluation/score.py`, the scorer. `evaluation/runs/1/score.txt`, the first score. `evaluation/failure.md`, your write-up. The rules: section 3.3, "Start the evaluation set", and day 2's section 2.2, "Write the system prompt on purpose".

## Steps

1. Run `code prompts/system.txt evaluation/runs/1/score.txt evaluation/failure.md`. In `evaluation/runs/1/score.txt`, you should see `form` at 0.00 for precision and recall.
2. Make the three changes of this table by hand. Save each file.

| Part | Write this | Why |
|---|---|---|
| 1. `Note:` and `Field:` in `evaluation/failure.md` | `Note: 0147` and `Field: form` | In `evaluation/runs/1/score.txt`, all 20 wrong values are in `form`. Each label gives the right value: the form number only, such as "1040". Each reply adds "Form". So any note shows the failure, such as 0147. Section 3.3, the list "Score the fields, not the note": "Per field, the score names the instruction to change" |
| 2. `Cause:` in `evaluation/failure.md` | `Cause: 11, 17` | Lines 11 and 17 of `prompts/system.txt` are the replies of the two examples. Both write `"form": "Form 1040"`. No line says how to write a form, so the model copies the examples. Day 2 showed the same with amounts. Day 2, section 2.2, the list "Examples teach the shape": "Every example with an amount teaches that notes have amounts" |
| 3. `prompts/system.txt` | In lines 11 and 17, write `"form": "1040"` in place of `"form": "Form 1040"`. | The model copies the examples. With "1040" in them, it writes the form number only, as the labels do. Day 2, section 2.2, under "Revise by editing the prompt, then re-score the whole set.": "A loop: run the set, score it, edit the prompt" |

Then run `python3 evaluation/score.py`. For a new prompt, it sends the 20 notes to the model. You should see `form` above 0.00 in the line that ends with `(this prompt)`. If not, step 3's check says what to do next.

3. Run `git add prompts/system.txt evaluation`. Then run `git commit -m "Revise the prompt once"`. Then run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then do this step again.

**Answer:** `~/practice/week-01/day-03/answers/score-the-prompt/`, whose `commands.sh` ends with `Done:`.

## Afterwards, together

- Why can a labelled set find what the teammate's five replies did not?
- When would a new line about the form be a better change than the examples?
- Your second score is one run. Which differences come from your change, and which from the run?
