# Exercise: Check replies against a schema and your own check

After this exercise, you can check each reply against the schema and your own check, and count a bad reply as a failure.

**Scenario:** Five of eight replies failed `check_reply` in `extractor.py`. So a teammate changed the schema and `check_reply`, and now two fail.

**Success criterion:** from `lab`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-03/validate-replies/lab`, in VS Code. In the Explorer, it is `week-01 › day-03 › validate-replies › lab`. Each path in this exercise starts there. Do not use AI tools.

**Start from:** `lab`, the lab after its run 2, with the teammate's commit on top. Run `python3 ~/practice/reset.py validate-replies`. It prints `validate-replies is back as it was supplied.` Then run `cd ~/practice/week-01/day-03/validate-replies/lab`. To start again, run the same reset. It removes your changes.

**What you have:** `schema/output.schema.json`, `extractor.py`, and eight replies in `replies/`, each named for its note in `notes/`. `count_failures.py` counts the failures. `../check.py` is the check. The course made up every note. The rules are in section 3.1 of day 3, "Ask for structured output".

## Steps

1. Run `code schema/output.schema.json extractor.py`. Then run `python3 count_failures.py`. You should see `Failures: 2 of 8 replies.`
2. Make the three changes of this table, in order.

| Change | Write this | Why |
|---|---|---|
| 1. `next_action` | In `schema/output.schema.json`, make line 10 `"next_action": {"type": "string"}` | Note 0138 ends "Wait for the call.", but reply 0138 gives null. Every note states its next action, so null there is wrong. Section 3.1, below the table of fields: "Only amount_in_question may be null, because the lab's notes always state the other four fields." |
| 2. An amount as text | In `extractor.py`, remove lines 29 to 34, from `# The model sometimes` | These lines turn "40,000 of 95,000" in reply 0105 into 4000095000, a wrong amount. A guess can be wrong, so the reply must fail instead. Section 3.1, below the second figure: "a reply that fails is counted as a failure, never repaired by guessing" |
| 3. Your own check | In `extractor.py`, put `import datetime` above `import json`. Put the lines below just above `return fields`, after the schema check | Reply 0130 gives tax year 2203, but note 0130 names 2023. The schema passes any integer, so only your own check can fail a year that has not begun. After the schema check, `tax_year` is an integer, so `>` can compare it with this year. Section 3.1, in the list above the second figure: "Tax year 2203 passes the schema, not your own check" |

```python
    if fields["tax_year"] > datetime.date.today().year:
        raise ExtractionFailed("the tax year is after this year")
```

Save each file. Run `python3 count_failures.py` again. You should see `Failures: 6 of 8 replies.`

3. Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then run the check again.

**Answer:** `~/practice/week-01/day-03/answers/validate-replies/` holds the fixed files, `decisions.md`, and `commands.sh`, which ends with `Done:`.

## Afterwards, together

- The comment that you removed names "18,400", one clear number. Should `check_reply` turn it into 18400, and why?
- When would `next_action` need null too?
- Which wrong tax year does your own check still pass, and what would stop it?
