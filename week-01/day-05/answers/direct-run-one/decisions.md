# The course's answer: each answer, its reason, and what else the check accepts

`agent-run/` holds run 1 as two coding agents made it, one kept run each, on 2026-10-30: Codex and
Claude Code. `agent-run/README.md` says what each run is. The answer here is for the Codex run,
which `commands.sh` copies. The check reads the run that is in `lab/`, so the rules below hold for
the run that your agent makes.

| Your answer | The answer here | Why: the reason, then the notebook's line | What else the check accepts |
|---|---|---|---|
| When your agent asks | No, if it asks to break the prompt's Constraints. Yes, if not. | A yes lets it do that, such as a call to the model. Section 5.1, run 1's Constraints: "Do not call any model." | The check does not read the session. It reads what the run left. |
| The done-when, run by you | `python3 -m pytest tests/test_schema.py`, in your terminal. Its last line: `22 passed in 0.03s`. | The agent's report is only its word. Your own run shows the result. Section 5.2, list "For every run, yourself": "Run the done-when in your own terminal" | `pytest tests/test_schema.py`, with `-q` or without it. The check runs the done-when itself. |
| What you stage | `files = "schema tests"` in cell 2, or `git add schema tests` | The Constraints let the run change only these folders. Section 5.1, run 1's Constraints: "Do not edit anything outside schema/ and tests/." | Each folder in its own run of cell 2, in any order. A file that the run left outside `schema/` and `tests/` can stay out. |
| What you read first | `form = "--staged"` in cell 2, which opens `tests.diff`. Or `git diff --staged -- tests`. | The agent wrote the tests that decide whether it passes. Section 5.2, the same list: "Read the test files' diff first". The plain form misses staged files. Day 4, section 4.3, list "The trap: the plain form": "Shows only changes still unstaged" | Any form. The check does not read how you read the diff. |
| Done | `Done: met` | Your pytest run passed with both tests. `test_missing_field_fails` takes each required field out of an output, `amount_in_question` among them, and expects an error. `test_null_amount_passes` sets `amount_in_question` to None and expects no error. Both load the run's schema, `schema/case_notes.schema.json`. So run 1 holds both parts of its done-when. Section 5.1, run 1's Done-when: "one output that must fail (amount_in_question missing) and one that must pass with amount_in_question null" | Yes or No at the start of Done. "not yet met" does not count: start Done with met or not met. For a run that misses a part, `Done: not met` is the right answer. Then the check asks you to direct and check run 1 again. It prints `Done:` only for a run that meets its done-when. |
| Proof | `Proof: python3 -m pytest tests/test_schema.py printed 22 passed in 0.03s. Must fail: test_missing_field_fails. Null passes: test_null_amount_passes.` | The table's rule, with the values of this run: the command, its last line, and the name of each test. Anyone can run it again, and find each test. Section 5.2, list "Have it show evidence": "The command it ran, and what it returned" | Other words around them, with each test name after its own label. Both names with no labels at all. The counts of the last line, with its time and = signs or not. A second count too, such as the count after your own change to the schema. A case with its `[...]`, such as `test_missing_field_fails[amount_in_question]`. For the Claude Code run: `19 passed`, `test_missing_amount_fails` and `test_null_amount_passes`, not its test of the schema itself. |
| The commit | One commit of `schema/` and `tests/`, with the message of step 3 | A commit records the run that you accepted. Section 5.2, the answer to its Check: "the commit and the stored result are evidence." | Two commits, or a commit that the agent made. A file that the run left outside `schema/` and `tests/` can stay out of the commit. Git leaves `run-1-record.md` and `tests.diff` out of each commit. |

## How the check decides Done

The check runs the done-when on your run. Then it runs the same tests on a copy of `lab`, four
times. Each time, it makes one change to each JSON file in `schema/` that gives
`amount_in_question` a schema:

- The first change takes `amount_in_question` out of the required fields. A test that holds "one
  output that must fail (amount_in_question missing)" fails after it.
- The second change does not let `amount_in_question` be null. A test that holds "one that must
  pass with amount_in_question null" fails after it.
- After each of the two, a change in form only, which keeps what the schema accepts. For the
  first part, an `allOf` requires `amount_in_question`. For the second part, the schema of
  `amount_in_question` goes into an `anyOf`. A test that holds the part does not fail after it.

Run 1 meets its done-when when the tests pass on your run, and a test holds each part. A test case
that is not there after a change counts as a test that fails. Your Proof must name a test that holds
each part. Where it writes a part's label, that test's name follows the label. For a run that fails
its done-when or misses a part, the check never asks for a commit: no one accepts such a run.

- **Tests on their own copy of the schema.** The tests hold both outputs, and pytest passes. But
  they do not test the schema in `schema/`, so no change to it makes a test fail. The check says
  "not met".
- **A schema that is not a JSON file in `schema/`,** such as a Python file. The check cannot
  change it, so it cannot tell. Then a Done of met stands, and your Proof must name a test of the
  run that passes. The Done line says that your Done stands. A Done of not met asks for a new run,
  as for any run.
- **A test of the schema itself,** such as `"amount_in_question" in SCHEMA["required"]`. It fails
  after the first change, and also after the change in form only. So the check counts it for no
  part. The Claude Code run has one, `test_schema_names_exactly_the_five_fields`. Its must-fail
  test is `test_missing_amount_fails`.
- **A test with cases from the list of required fields in the schema,** such as
  `test_missing_field_fails` in the Codex run. After the first change, its case for
  `amount_in_question` is not there, so the check counts that case for the must-fail part. After
  the change in form only, the case is not there either. It does not fail, so it still counts.

## For the debrief

- **If pytest passes, when would Done still be not met?** Start from the cases above: tests on
  their own copy of the schema, and a test of the schema itself. Then the Codex run's must-fail
  case: when the schema no longer requires `amount_in_question`, the case is not there, and pytest
  still passes.
- **How would you stop run 2 from editing your accepted tests?** Section 5.2, list "For every run,
  yourself": "Make the tests read-only: a deny rule". "In the lab that is a deny rule in the
  agent's configuration: a setting that blocks its edits to the files it names." For Claude Code,
  `claude-settings.json` here adds `"Edit(/tests/test_schema.py)"` to the list `"deny"` of
  `.claude/settings.json`. It names the file, not `tests/`, as run 2 adds `tests/test_extractor.py`.
  Codex does not read `.claude/settings.json`, and the course found no Codex setting for one file
  ("Agent approvals & security", https://learn.chatgpt.com/docs/agent-approvals-security, read
  2026-10-30). With Codex, read the test files' diff after each run. The exercise asks for no deny
  rule: the steps had no room for it, and Codex does not read it.
- **What did you not check in run 1, and who needs to know?** The report of section 5.2 has four
  fields: "done, proof, scope, not verified". Your report holds the first two. The course did not
  compare each rule of `docs/fields.md` with the schema, and did not read the agent's session for a
  model call.

## The notebook's words, kept in the quotes

The linter reads this finding. The file keeps the notebook's words.

- `run1-prompt.txt` holds the four parts of the table of section 5.1, with its four semicolons.
  The learner sends the file to the agent as it is, so it has no quote marks. The kept runs got
  the same words on four lines. The file now wraps them at 90 characters.
