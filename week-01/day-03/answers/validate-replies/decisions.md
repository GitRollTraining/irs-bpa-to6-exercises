# The course's answer: each change and its reason

The answer makes the three changes of the table in step 2. Each rests on a line of the notebook of day 3, section 3.1, "Ask for structured output". The steps name where each line is. The table of fields sits under the heading "Every field is required, and only the amount may be null." The list and the second figure sit under "Validate every reply in your own code anyway." The check gives the eight replies to the changed `check_reply`, and more replies that it makes from them. It also reads the changed schema with sample replies. When it finds nothing else, it runs the lab's tests. The exercise asks for no commit: the Goal and section 3.1 need none, so the check reads `lab` as it is.

| Change | The answer | Its reason, then the notebook's line | The check also accepts |
|---|---|---|---|
| 1. `next_action` | In `schema/output.schema.json`, line 10 is `"next_action": {"type": "string"}`, as on `main`. | Note 0138 ends "Wait for the call.", but reply 0138 gives null. Every note states its next action, so null there is wrong. Section 3.1, below the table of fields: "Only amount_in_question may be null, because the lab's notes always state the other four fields." | Any schema that lets only `amount_in_question` be null. It keeps the rest of the contract: all five fields required, no key of its own, and the types of the table of fields. A check in `check_reply` alone is not enough, because the extractor also sends this schema to the model. |
| 2. An amount as text | Lines 29 to 34 of `extractor.py`, from `# The model sometimes`, are gone. Then the schema fails replies 0104 and 0105. | These lines turn "40,000 of 95,000" in reply 0105 into 4000095000, a wrong amount. A guess can be wrong, so the reply must fail instead. Section 3.1, below the second figure: "a reply that fails is counted as a failure, never repaired by guessing" | Any `check_reply` that fails a reply with an amount as text, and returns each reply that passes as it came. One that raises `ExtractionFailed` for an amount as text also passes. |
| 3. Your own check | `import datetime` above `import json`. Just above `return fields`, after the schema check: `if fields["tax_year"] > datetime.date.today().year:`, then `raise ExtractionFailed("the tax year is after this year")`. | Reply 0130 gives tax year 2203, but note 0130 names 2023. The schema passes any integer, so only your own check can fail a year that has not begun. After the schema check, `tax_year` is an integer, so `>` can compare it with this year. Before it, `tax_year` can be missing or text, and `>` stops with an error. Section 3.1, in the list above the second figure: "Tax year 2203 passes the schema, not your own check". The second figure also puts your own check after the schema. | Any check after the schema check that fails tax year 2203, and passes 2020 to 2023, the years that the notes in `notes/` name. A range from 2000 to this year also passes. So does a range in the schema, with `"minimum"` and `"maximum"`. |

## Why only a year after this year

The notebook names one bad tax year, 2203, and no range. A year after this year has not begun, so it cannot be the tax year of a note. So the answer fails only such a year. No cell above gives a first year, so the answer sets none. The debrief starts from this answer.

## For the debrief

- "18,400": the text holds one clear number, so 18400 is no guess. But the reply still fails the schema, and section 3.1 counts such a reply as a failure. The count then shows how often the model breaks the schema. Each new form of text also needs a new rule, and "40,000 of 95,000" in reply 0105 shows where such a rule starts to guess. The check fails a reply whose amount is "18,400" too.
- `next_action`: when your own data can leave it out. Section 3.1, below the table of fields: "A field that can be absent in your own data needs null too." The lab's notes always state it, so here it stays a string. Notes 0119 and 0132 end with an action in the past, such as "Requested the general ledger.". The field list, `docs/fields.md`, gives `next_action` as "what happens next, as the note says it", so the reply gives that action, not null.
- Tax years: the answer passes 2022 for a note that names 2023, and 1023, a typo. A first year, such as 2000, stops 1023. Only a look at the note stops 2022.

## The replies

Replies 0102 and 0147 are the lab's recorded replies, from `tests/recorded/`. The course wrote the other six by hand, each to show a failure, as the lab's `tests/test_schema.py` writes its outputs by hand.

## The words inside the quotes

The quotes keep the notebook's words. The linter finds these things in them. They stay as the notebook has them.

| The words | What the linter finds |
|---|---|
| "is counted", in the rule of row 2 | passive voice |
| "repaired", in the rule of row 2 | a second word for "fix" |
| "validates", in a line that the check quotes: "So the extractor validates every reply against the schema and against simple checks of its own" | a second word for "check" |
| "is required", in the first heading above | passive voice |
| "Validate", in the second heading above | a second word for "check" |

The steps name the table, the list and the figure, not these two headings, so the learner's text keeps no more of these findings.
