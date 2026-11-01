# Exercise: Direct the first run and check it yourself

After this exercise, you can direct a coding agent's run, and check it yourself before you accept it.

**Scenario:** You direct run 1, and your agent reports done. Check that claim yourself.

**Success criterion:** from `lab`, `python3 ../check.py` prints `Done:`.

**Where you work:** `~/practice/week-01/day-05/direct-run-one/lab`, in VS Code and a terminal, with Codex or Claude Code. In the Explorer: week-01 › day-05 › direct-run-one › lab. Each path starts there.

**Start from:** the lab before run 1. Run `python3 ~/practice/reset.py direct-run-one`. It prints `direct-run-one is back as it was supplied.` Run `cd ~/practice/week-01/day-05/direct-run-one/lab`. To start again, run the reset again. It removes the agent's run.

**What you have:** in `lab`, run 1's prompt `run1-prompt.txt` and your report `run-1-record.md`. Rules: 5.1, "A directing prompt with a done-when", 5.2, "Check the done-when yourself", and day 4's 4.3, "Compare before and after you commit".

## Steps

1. Run `code run1-prompt.txt run-1-record.md`. Both files open.
2. Direct and check run 1.
   1. Start your agent: `codex` or `claude`. Trust this folder: its settings start no program.
   2. Paste all of `run1-prompt.txt` as one message. If the agent asks to break the Constraints, answer no: a yes lets it do that. Section 5.1, run 1's Constraints: "Do not call any model. Do not edit anything outside schema/ and tests/."
   3. When it reports, type `/exit`. Run the done-when yourself: `python3 -m pytest tests/test_schema.py`. The agent's report is only its word. Section 5.2, list "For every run, yourself": "Run the done-when in your own terminal".
   4. Run `git add schema tests`, the run's folders.
   5. Run `git diff --staged -- tests`. The agent wrote the tests that decide whether it passes. The same list: "Read the test files' diff first". The plain form misses staged files. Day 4's 4.3, list "The trap: the plain form": "Shows only changes still unstaged". You should see each test line after `+`.
3. In the diff, find both tests of the Done row. Press q. In `run-1-record.md`, write this table's lines. Save the file. If Done is not met, direct and check run 1 again. If Done is met, run `git commit -m "Accept run 1"`. Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names.

| Line | Write this | Why |
|---|---|---|
| Done | `Done: met` if your pytest run passed with both tests. Else `Done: not met`. | The done-when asks for two tests. One expects an error when an output lacks `amount_in_question`, or each required field in turn. The other sets `amount_in_question` to None, Python's null, and expects no error. Section 5.1, run 1's Done-when: "one output that must fail (amount_in_question missing) and one that must pass with amount_in_question null" |
| Proof | `Proof: python3 -m pytest tests/test_schema.py printed <its last line>. Must fail: <test name>. Null passes: <test name>.` | Anyone can run it again, and find each test. Section 5.2, list "Have it show evidence": "The command it ran, and what it returned" |

**Answer:** `~/practice/week-01/day-05/answers/direct-run-one/` holds `decisions.md` and `commands.sh`, which ends with `Done:`.

## Afterwards, together

- If pytest passes, when would Done still be not met?
- How would you stop run 2 from editing your accepted tests?
- What did you not check in run 1, and who needs to know?
