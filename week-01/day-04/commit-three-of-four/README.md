# Exercise: Commit three changes and leave the fourth out

After this exercise, you can commit only the changes that you asked an agent for, and keep the extractor's log out of the history.

**Scenario:** You asked a coding agent to log each failed reply by the note's number only. The agent changed four files and ran the extractor once.

**Success criterion:** from `extractor`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-04/commit-three-of-four/extractor`, in VS Code. In the Explorer, it is week-01 › day-04 › commit-three-of-four › extractor. Each path in this exercise starts there. Do not use AI tools.

**Start from:** the lab after the agent's run. Run `python3 ~/practice/reset.py commit-three-of-four`. It prints `commit-three-of-four is back as it was supplied.` Then run `cd ~/practice/week-01/day-04/commit-three-of-four/extractor`. To start again, run the reset, which removes your changes and your commits.

**What you have:** the extractor's log `logs/extractor.log` and `.gitignore`. `../agent-session.txt` holds your request and the agent's report. The rules are in section 4.1 of day 4's notebook, "A history you can read".

## Steps

1. Run `code ../agent-session.txt logs/extractor.log .gitignore`. Then run `git status --short`. You should see `M` for four files that changed since the last commit. `??` marks the untracked `logs/`: no commit holds it.
2. Do what this table says. Save `.gitignore`. Then run `git add extractor.py tests/test_extractor.py README.md .gitignore`.

   | Change | What to do | Why, in section 4.1 |
   |---|---|---|
   | `extractor.py`, `tests/test_extractor.py`, `README.md` | Stage each. | `../agent-session.txt` asks for all three: a log line for each failed reply, a test and a `README.md` line. The table under "Skipping staging lets an agent's stray edit in.", row Who chooses: "You choose which changes go in". |
   | `model.py` | Do not stage it. | Line 1 of `logs/extractor.log` holds the whole note, but you asked for "the note's number only". The change to `model.py`, a debugging print, wrote it. The same table, row The debugging print: with git add, then git commit, it "Can stay out". |
   | `logs/` | Add the line `logs/` at the end of `.gitignore`. Stage `.gitignore`. | A commit of `logs/` keeps a whole note in the history. Your line stops Git listing and adding `logs/`. Committed, it does so in each clone. The heading "Keep the logs out: a pushed commit is very hard to take back." Below it: "A .gitignore file lists patterns of files Git will not offer to add." |

   Run `git status --short`. You should see `M` in the first column, staged, for your four files, and ` M model.py`, not staged. `?? logs/` is gone. To unstage a file, run `git restore --staged` with its path.
3. Run `git commit -m "Log each failed reply by note number"`. Then run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then run the check again.

**Answer:** `~/practice/week-01/day-04/answers/commit-three-of-four/` holds `decisions.md` and `commands.sh`, which ends with `Done:`.

## Afterwards, together

- When is `git commit -a` safe, and why?
- Would staging by path keep out a stray edit in `extractor.py`? Why?
- Which files of your own work belong in `.gitignore`, and why?
