# Exercise: Choose a model and two levels, and record why

After this exercise, you can choose a model and a reasoning level for a task, and record the reason for each.

**Scenario:** A teammate wants a more capable model for the extractor. Your coding agent has two tasks next.

**Success criterion:** from `lab`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-02/model-and-reasoning-level/lab`, in VS Code. In the Explorer, it is week-01 › day-02 › model-and-reasoning-level › lab. Each path in this exercise starts there. Do not use AI tools.

**Start from:** the lab's saved state `run2`, after run 2. Run `python3 ~/practice/reset.py model-and-reasoning-level`. It prints `model-and-reasoning-level is back as it was supplied.` Then run `cd ~/practice/week-01/day-02/model-and-reasoning-level/lab`. To start again, run the same reset. It removes your commits.

**What you have:** in `lab`, `docs/model-scores.md` with the scores of the models haiku and sonnet, `docs/next-tasks.md` with the tasks and the agents' commands, and your table, `docs/pull-request.md`. `../check.py` is the check.

## Steps

1. Run `git log --oneline --no-decorate`. You should see six commits. The newest adds the three files in `docs`. Each commit in step 3 adds one.
2. Fill in the table in `docs/pull-request.md`. Copy Start with and Reason from this table. With Codex, write `codex -c model_reasoning_effort=medium` and `codex -c model_reasoning_effort=low` in place of the two commands. Each Reason is one of three. Section 2.3, under "Two dials": "Every reason for a choice is one of three: capability, speed or cost."

| Choice | Start with | Reason | Why |
|---|---|---|---|
| The extractor's model | `sonnet` | `capability` | In `docs/model-scores.md`, haiku got note 0104 wrong, and sonnet did not. So sonnet fixes a failure that the set shows: the one reason to move up. Section 2.3, under "The pull request names each model and level, and the reason.": "move up only for a failure the set shows it fixes". |
| Task 1: notes that name two amounts or two tax years | `claude --effort medium` | `capability` | In `docs/next-tasks.md`, the rule of task 1 can change the reply for any note, so you score the whole set again. Work that you must check so well gets a higher level, but not high, the top one, which can overthink. Section 2.3, under the same heading: "work where verification matters or edge cases are likely". Under "Two dials": "the top level can overthink, so test it". |
| Task 2: three tests of bad replies | `claude --effort low` | `speed` | In `docs/next-tasks.md`, you read the three tests line by line, so you check each result yourself. Such small work gets the lowest level, which is the fastest. Section 2.3, under the same heading: "quick exchanges where you review each result". |

3. Save the file. Run `git add docs/pull-request.md`. Then run `git commit -m "Choose the model and levels"`. Then run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then do this step again.

**Answer:** `~/practice/week-01/day-02/answers/model-and-reasoning-level/` holds the filled-in table, `decisions.md` and `commands.sh`.

## Afterwards, together

- When would haiku be the better choice, and why?
- Task 2 also changes a file. When would it need a higher level?
- Capability, speed or cost: which reason decides most often in your own work, and why?
