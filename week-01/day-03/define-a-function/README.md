# Exercise: Define one function, and test both cases

After this exercise, you can describe a function for the model, and test it where a call is right and where none is.

**Scenario:** A teammate wrote the functions that the model can ask for when a caseworker asks about case notes. Fix the list before anyone uses it.

**Success criterion:** from `lab`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-03/define-a-function/lab`, in the day's notebook or in a terminal. In the Explorer, it is week-01 › day-03 › define-a-function › lab. Each path starts there. `ask.py` calls the model. Use no other AI tool.

**Start from:** the lab after the data-rules check, with a teammate's commit. Run `python3 ~/practice/reset.py define-a-function`. It prints `define-a-function is back as it was supplied.` Then run `cd ~/practice/week-01/day-03/define-a-function/lab`. To start again, run the same reset. It removes your changes and replies.

**What you have:** `functions.json`, the function list, which you change. `tools.py`, the code of each function. `ask.py`, which sends two questions and saves the replies. The rules are in section 3.2, Describe a function.

## Steps

1. Run `code functions.json`. The function list opens in the editor.
2. Make these three changes by hand. Copy each `\"`: JSON needs a `\` before a quote inside a text.

| Part | Write this | Why |
|---|---|---|
| 1. `add_follow_up` | Remove its definition, from its `{` to its `},`. | In `tools.py`, it writes the next action into the case file. IRS policy keeps such actions under a person's oversight. Section 3.2, the table of functions, row "Record an action on a case": "No: that call belongs to a person". |
| 2. The `description` of `lookup_form` | In place of `TODO`: `Gives the title of a tax form, such as \"U.S. Individual Income Tax Return\" for 1040. Call it only when a question asks what a form is, and the note does not say it. It reads a table of titles. It writes nothing.` | The model cannot see `tools.py`. So this text says what the function does, when to call it, and that it writes nothing. Notes 0106 and 0147 name a form. Only the question about 0106 asks what a form is. Section 3.2, list "Describe each function": "Could an intern use it from that alone?" |
| 3. The `description` of `form_number` | In place of `TODO`: `The number of the form as the note writes it, without the word Form, such as \"5329\", \"1120-S\" or \"W-2\".` | `tools.py` finds the title of `5329`, but nothing for `Form 5329`. So the description says what to send. Section 3.2, the same list: "Its purpose, and each parameter". |

Save `functions.json`. Run `python3 ask.py`. You should see a call to `lookup_form` with `{"form_number": "5329"}` for note 0106, and no call for note 0147.

3. Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then run `python3 ask.py`. Then do this step again.

**Answer:** `~/practice/week-01/day-03/answers/define-a-function/` holds the finished list, the kept replies, `decisions.md` and `commands.sh`.

## Afterwards, together

- When could `add_follow_up` go back on the list, and why?
- A teammate wants to add `read_note(note_id)`, which reads any note. Who should choose `note_id`, and why?
- Which third question would you add to test the list, and why?
