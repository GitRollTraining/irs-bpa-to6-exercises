# Exercise: Read one change in every view, before and after

After this exercise, you can read a coding agent's change in each form of `git diff`, before and after you commit it.

**Scenario:** A coding agent made one more run in the lab. It staged part of its change.

**Success criterion:** from `lab`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-04/diff-views/lab`, with Git. In the Explorer, it is week-01 › day-04 › diff-views › lab. Each path in this exercise starts there. Do not use AI tools.

**Start from:** the lab at its saved state `run2`, plus the agent's change. Run `python3 ~/practice/reset.py diff-views`. It prints `diff-views is back as it was supplied.` Then run `cd ~/practice/week-01/day-04/diff-views/lab`. To start again, run the same reset. It removes your commits.

**What you have:** in `lab`, `docs/directing-prompt.md`: your directing prompt, and the agent's report. `../check.py` is the check. The rules are in section 4.3, "Compare before and after you commit".

## Steps

1. Run `code docs/directing-prompt.md`. It opens the directing prompt and the report.
2. Run `git diff` with the form of each row below, in order. `--name-status` lists only the files, and M marks a changed file. Before row 3, run `git restore --staged prompts/system.txt`. It takes the file out of the staging area, and keeps its change on disk. Then run `git add extractor.py`. Before row 4, run `git commit -m "Fail a reply whose amount is negative"`.

| Row | Form | You should see | Why, in section 4.3 |
|---|---|---|---|
| 1 | `--name-status` | Only `extractor.py` | This form compares the files on disk with the staging area. So it misses what the agent staged. The list "The trap: the plain form": "Shows only changes still unstaged". |
| 2 | `HEAD --name-status` | All three files | This form compares the files on disk with the last commit, staged or not. It shows `prompts/system.txt`, which the agent staged but did not report. The directing prompt does not allow that file, so you unstage it. Under "Start wide, then point --exit-code at HEAD for the tests.": "a file outside what the directing prompt allowed is a finding". |
| 3 | `--staged --name-status` | `extractor.py` and `tests/test_extractor.py` | This form compares the staging area with the last commit: what your commit will hold. The directing prompt asks for both changes, but the agent did not stage `extractor.py`. So you stage it. The list "The trap: the plain form": "Run git diff --staged before every commit". |
| 4 | `HEAD^ HEAD --name-status` | `extractor.py` and `tests/test_extractor.py` again | `HEAD` is now your commit, and `HEAD^` the one before. So this form shows what your commit changed. The list "A diff shows lines": "HEAD: the commit you are on". "HEAD^: the one before". |

3. Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then run the check again.

**Answer:** `~/practice/week-01/day-04/answers/diff-views/` holds `decisions.md`, and `commands.sh`, which ends with `Done:`.

## Afterwards, together

- When would the plain form show every file of the agent's change?
- Would `git diff --exit-code -- tests/` catch this run's test change? Why?
- When would the change to `prompts/system.txt` go into a commit, and why?
