# Exercise: Send two notes five times each, and record what the note does not state

After this exercise, you can see the model sample its replies, and find values that the note does not state.

**Scenario:** The extractor sends each note to its model once. You send two notes five times each.

**Success criterion:** from `lab`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-02/same-note-five-times/lab`, in the day's notebook or in a terminal. In the Explorer, it is week-01 › day-02 › same-note-five-times › lab. Each path in this exercise starts there. `send_five.py` calls the model. Use no other AI tool.

**Start from:** the lab's saved state `configured`, with the data-rules check committed. Run `python3 ~/practice/reset.py same-note-five-times`. It prints `same-note-five-times is back as it was supplied.` Run `cd ~/practice/week-01/day-02/same-note-five-times/lab`. To start again, run the same reset. It removes your record and replies.

**What you have:** the system prompt `prompt.txt`, `notes/0147.txt` and `notes/0104.txt`, `send_five.py`, which saves the replies in `replies/`, and your record, `record.md`. `../check.py` is the check.

## Steps

1. Run `code prompt.txt record.md`. It opens the prompt and your record.
2. Run `python3 send_five.py 0147 0104`. You should see `Note 0104: reply 1 2 3 4 5 saved.` Then run `code field-by-field.txt`: each note, its dates and numbers, and the five values of each field.
3. In `field-by-field.txt`, find the note and the field of each row of `record.md`. Each of its five values comes from one reply. In the row, write the numbers of the replies that this table names, such as `2, 4` for replies 2 and 4. If no reply fits, write `none`. Save the file. Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then run the check again.

| Row of `record.md` | What to write | Why |
|---|---|---|
| 0147, `next_action` | The numbers of the replies whose value has a date, such as 2026-11-30, or another number that the note does not have | Note 0147 says only "Follow up in 30 days". It gives no date. So a reply with a date adds a fact that is not in the note: the model wrote a likely date. Section 2.1, under "A fluent answer is not a known answer.": "It writes the likeliest text, not a lookup." |
| 0104, `amount_in_question` | The numbers of the replies whose value is not null. null, with no quotes, means "no value" | Note 0104 says "No amount yet", so the right value is null. A reply with text, such as `"None yet"`, puts words in a field that must stay empty. Section 2.1, under the same heading: "text where null belongs" |

**Answer:** `~/practice/week-01/day-02/answers/same-note-five-times/` holds the replies of 2026-10-20, from the course's run that section 2.1 names, and their record. In section 2.1, "all ten of its replies" are these five replies to note 0104 and five from a second run. The folder also holds `decisions.md` and `commands.sh`, which ends with `Done:`. `~/practice/week-01/day-02/answers/same-note-five-times/run-2026-10-30/` holds a later run, with its record.

## Afterwards, together

Note 0147 names an amount, and note 0104 names none. What came back in `amount_in_question` for each, and why? Which fields changed across the five replies to the same note, and why? In which other field did a reply give a value that the note does not state?
