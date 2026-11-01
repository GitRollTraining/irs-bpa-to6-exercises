# The course's answer: each choice, and the rule it rests on

Each rule is in section 2.3 of the notebook of the day, "Choose the model and its reasoning level". The facts are in `docs/model-scores.md` and `docs/next-tasks.md`. The class starts the debrief from the answer in the second column.

| Choice | The course's answer | The rule, and the facts | The check also accepts |
|---|---|---|---|
| The extractor's model | sonnet. Reason: capability. | See the table under "The pull request names each model and level, and the reason." Its row The extractor's model: "Efficiency-first; move up only for a failure the set shows it fixes". The Check question below it: "Cheaper and holding the score is the better choice." Haiku gave an amount for note 0104, which names no amount, in two of its five replies, and sonnet gave null in each. Section 2.1 calls a change between replies normal: "Sent again, a different reply is a normal part of how it works." But an amount for a note that names none is a failure in any reply. In section 2.1, a hallucination is "output that appears coherent and plausible but does not reflect factual data". Section 2.2 says that the null rule reduces hallucinations, and does not "eliminate them entirely". So the set shows a failure that sonnet fixes. Haiku is cheaper, but it does not hold the score: 16 of 20, and sonnet 17. Neither rule gives a number of failures or dollars, so one failure is enough, at three times the cost. | No other model, and no other reason. Sonnet is slower and costs more, so speed and cost are not reasons for it. |
| Task 1: notes that name two amounts or two tax years | Medium: `claude --effort medium` or `codex -c model_reasoning_effort=medium`. Reason: capability. | Below the same table: "a higher one with work where verification matters or edge cases are likely". The row of run 2: "Edge cases: the set's notes". Task 1 is one rule, but its notes 0105, 0122 and 0137 are edge cases of the set. Only a new score of the whole set shows if the rule works. | High, with low for task 2. The table names "A lower level" and "A higher level", so the check reads the two levels against each other. The level of task 1 must be above the level of task 2. The answer starts at medium: under "Two dials", "the top level can overthink, so test it". |
| Task 2: three tests of bad replies | Low: `claude --effort low` or `codex -c model_reasoning_effort=low`. Reason: speed. | Below the same table: "the lowest with quick exchanges where you review each result". The row of run 1: "Small; you read all of it". Under "Two dials": "Lower: faster and cheaper for straightforward tasks". Task 2 is three short tests in one file. They read no note and call no model, and you read every line. | Cost as the reason. Medium, with high for task 1. |

The check accepts the command of either coding agent, and both commands in one cell at the same level.

In the exercise `system-prompt`, the course's two runs of haiku gave null for note 0104. In `docs/model-scores.md`, haiku also gave null in three of its five replies.

## What the check does not accept

- Haiku for the extractor. The set shows a failure, note 0104 in two of five replies, that sonnet fixes.
- Speed or cost as the reason for sonnet. Under "Two dials", these reasons are for the faster and cheaper choice: "it needs its answer quickly, or it runs often enough that cost matters".
- A level for task 1 that is not above the level for task 2.
- Capability as the reason for the level of task 2, and speed or cost as the reason for the level of task 1. Under "Two dials", capability is the reason for more: "the task is hard enough to need more capability".
- A level word with no command, such as "a higher level". The step asks for the command that starts the session.
- A level other than low, medium or high, such as xhigh or max. `docs/next-tasks.md` gives the three levels that both agents take.

The check reads the reason in each row: capability, speed or cost. The facts behind each reason are in the third column. The class talks them through.

## Quotes that keep the words of the notebook

Two quotes in the table above keep a semicolon, as the notebook has them:

- "Efficiency-first; move up only for a failure the set shows it fixes"
- "Small; you read all of it"

The steps of the exercise quote only the part of the first quote after its semicolon.
