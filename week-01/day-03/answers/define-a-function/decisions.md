# The course's answer: each change, and why

Each rule is a line of the notebook of day 3, section 3.2, Describe a function, in quotes. At the start, the check prints four lines: one for each change of step 2, and one for the replies.

| Part | The change | Why | The check also accepts |
|---|---|---|---|
| 1. `add_follow_up` | Remove its definition. | `tools.py` shows that it adds a line to `cases/<note_id>.txt`, the case file. The caseworker reads that file to know what to do next. So a call writes an action into the case file. IRS policy keeps such actions under a person's oversight. Section 3.2, the table of functions, row "Record an action on a case": "No: that call belongs to a person". A good description does not change who decides. | Nothing else. The list may offer only `lookup_form`. `add_follow_up` under a new name fails too, because `tools.py` has no function with that name. |
| 2. The description of `lookup_form` | `Gives the title of a tax form, such as \"U.S. Individual Income Tax Return\" for 1040. Call it only when a question asks what a form is, and the note does not say it. It reads a table of titles. It writes nothing.` | The model cannot see `tools.py`. So the description says what the function does, when to call it, and that it writes nothing. Notes 0106 and 0147 name a form. Only the question about 0106 asks what a form is. Section 3.2, list "Describe each function": "Could an intern use it from that alone?" | Any words that are not empty and do not start with TODO. The two replies show if the words work. |
| 3. The description of `form_number` | `The number of the form as the note writes it, without the word Form, such as \"5329\", \"1120-S\" or \"W-2\".` | `tools.py` finds the title of "5329", but it finds nothing for "Form 5329". So the description says what to send. Section 3.2, the same list: "Its purpose, and each parameter". | Any words, as in part 2. |
| 4. The two questions | Run `python3 ask.py`. | One question needs a call, and one does not. A list that gets both right shows that the descriptions work. Section 3.2, list "Invented arguments": "Your set: notes where a call is right, and notes where none is". | For note 0106: one call to `lookup_form`, with arguments that match its schema, for which `tools.py` gives the title of Form 5329. For note 0147: no call, and any answer in text. |

## What else the check reads, and what it does not

- The schema of `lookup_form`, which step 2 does not change. The check accepts each schema with `"type": "object"` that accepts `{"form_number": "5329"}` and refuses a call with no `form_number` or with one more argument. It also refuses a schema with another property, or with no description of `form_number`.
- It does not read `strict`. The course's code that sends your list to the model (`model.py`) drops it. So the check tests each call against the schema in its place.
- It does not read the words of a description. Only the two replies test them.

## The two replies in `replies/`

The model made these two replies on 2026-10-30. `ask.py` sent this list to the model one time, on a computer of the course team, not in the hosted workspace of the course. `model.py` sent the two questions through Claude Code 2.1.314 to `haiku`, the model that `model-route.json` names. `ask.py` saved them in `replies/`. The course did not change them. A reply of the model can be different each time. The check accepts each reply that the rules allow.

## The quotes

Each quote keeps the words of the notebook, or of `system-prompt.txt` where the check names that file. The STE linter finds no problem inside them.
