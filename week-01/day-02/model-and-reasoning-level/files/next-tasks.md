# The next two tasks for your coding agent

The course made up these tasks. Your coding agent does each task in its own session.

## Where you set the level

You set the level when you start the session. The level stays for that session only. Use the command of your coding agent:

- Claude Code: `claude --effort <level>`
- Codex: `codex -c model_reasoning_effort=<level>`

In place of `<level>`, write low, medium or high. Both agents take these three levels. Low is the lowest of the three. Medium and high are both higher than low, and high is the highest.

In this exercise, you write each command in the pull request. You can write the command of either agent. You do not start the agent.

## Task 1: notes that name two amounts or two tax years

- What changes: one rule in the system prompt of the extractor, `prompts/system.txt`. The rule tells the model which amount and which tax year to give when a note names two.
- The notes it must get right: 0105 and 0122, which name two amounts each, and 0137, which names two tax years. The notes of the set that name no amount must give null.
- How you will check its work: you score the whole evaluation set again. The model reads the rule with every note, so the rule can change the reply for any note.

## Task 2: three tests of bad replies

- What changes: `tests/test_extractor.py`. The agent adds three tests, about 20 lines. Each test gives the extractor one wrong reply that the test holds: a `tax_year` as text, an extra field, or an empty reply. Each test expects a failure.
- The notes it must get right: none. The tests read no note and call no model.
- How you will check its work: you read the three tests, line by line. Then you run them with `python3 -m pytest -q`.
