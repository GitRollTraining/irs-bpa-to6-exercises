# The answer, row by row

The ten replies in `replies/` are the replies of the model, as they came on 2026-10-20. The model was haiku, behind the route of the kit, `model.py`, which runs `claude -p`. The replies came with `prompt.txt` and no schema. They are not replies from a stand-in. Section 2.1 names this run: "in the exercise run of 2026-10-20". Its "all ten of its replies" are the five replies to note 0104 here and the five of a second run on the same day. The course did not keep the second run.

`run-2026-10-30/` holds a run of 2026-10-30, with the same route, prompt and notes. Its `run.md` gives the version of `claude`, the model and the date. In that run, note 0104 got text in place of null in replies 1 and 3 only. Replies 2, 4 and 5 give null, and null is correct there. Replies 2, 3 and 4 to note 0147 add a date, 2026-11-29, that the note does not give. Reply 4 also gives the date of the run, 2026-10-30. The model gets the date of the run from `claude`, so "Follow up in 30 days" can come back as a date. On 2026-10-20, it came back as 2026-11-19.

`run-2026-10-30/record.md` names those replies, and the check accepts it. In next_action of note 0147, the check also accepts replies 1 and 5. Their values have new words but no new date or number, and a new word can add a fact. `run-2026-10-30/commands.sh` puts that run in `lab`, as `commands.sh` here does for the run of 2026-10-20.

Your run gives other replies. The check judges your two rows on your own replies, by the table in step 3.

| Row | Answer | Why | The check also accepts |
|---|---|---|---|
| 0147, next_action | 2, 5 | Replies 2 and 5 add a date, 2026-11-19. The note says "Follow up in 30 days", and gives no date. Section 2.1: "A fluent answer is not a known answer." | 1, 3 and 4 also, in any mix. "On the letter requesting business records" has new words, but no new date or number. |
| 0104, amount_in_question | 1, 2, 3, 4, 5 | Each reply gives text, such as "None stated" and "No amount yet". Note 0104 names no amount, so only null is right. Section 2.1: "No amount in the note: the reply is still fluent". It calls this "text where null belongs". | Nothing else |

How the check reads a value in a run of your own:

- next_action of note 0147: a value is in the row if it has a date or a number that the note does not have. Words of the note beside it do not change that. "1 month" for "30 days" is one: the note does not have the number 1. "Follow up in 30 days" only uses the words and numbers of the note, in its order, so it is not in the row. Each other value can be in the row or not.
- amount_in_question of note 0104: each value that is not null is in the row, also "No amount yet", in the words of the note. Null is not in the row. Null is the correct value there.
- A value with no JSON, or with no such field, can be in the row or not.

The other fields changed too. In the run of 2026-10-20, `tax_year`, `form` and `amount_in_question` of note 0147 changed their form, such as 2023 and "2023". Reply 4 to note 0104 gave two dates in next_action, 2026-10-20 and 2026-12-04. The debrief asks about these fields. In the run of 2026-10-30, note 0104 got text two times and null three times. The class talks about why.

The quotes keep the words of the notebook. The linter finds nothing in them.
