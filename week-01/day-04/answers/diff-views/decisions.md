# The course's answer: each row of the table, and its reason

The answer changes no file by hand. It changes the staging area, and it makes one commit.
`commands.sh` runs each row of the table in step 2. Each rule is in section 4.3 of the day's
notebook, "Compare before and after you commit".

| Row | The course's answer | The reason, then the notebook's line | The check also accepts |
|---|---|---|---|
| 1 | `git diff --name-status` shows `M extractor.py` only. | The plain form compares the files on disk with the staging area. The agent staged its changes to `prompts/system.txt` and `tests/test_extractor.py`, so this form does not show them. The list "The trap: the plain form": "Shows only changes still unstaged". | The check reads your commits, not the forms that you ran. |
| 2 | `git diff HEAD --name-status` shows all three files. `prompts/system.txt` stays out of the commit. | This form compares the files on disk with the last commit, staged or not. So it shows `prompts/system.txt`, which the report of the agent leaves out. The directing prompt allows a change to `extractor.py` and a test in `tests/test_extractor.py`, and says "Change no other file". Under "Start wide, then point --exit-code at HEAD for the tests.": "a file outside what the directing prompt allowed is a finding". | `prompts/system.txt` staged, not staged, or back as it was after `git restore prompts/system.txt`, if no commit holds it. |
| 3 | `git restore --staged prompts/system.txt`, then `git add extractor.py`. `git diff --staged --name-status` then shows `extractor.py` and `tests/test_extractor.py`. | This form compares the staging area with the last commit, so it shows what the commit will hold. The directing prompt asks for both changes, but the agent did not stage `extractor.py`. So you stage it. Without it, the new test fails. The list "The trap: the plain form": "Run git diff --staged before every commit". "It is exactly what the commit will hold". | Any change to `extractor.py` and any new test, if each test of the start stays and all the tests pass. Any number of commits. |
| 4 | After the commit, `git diff HEAD^ HEAD --name-status` shows the same two files. | `HEAD` is the commit that you made, and `HEAD^` the commit before it. The list "A diff shows lines": "HEAD: the commit you are on". "HEAD^: the one before". | The check reads your commits, not the forms that you ran. |

The debrief starts from this answer: the change to the system prompt stays on disk, and no commit
holds it. Section 4.3 decides on the file alone, before you read its lines.

For the three questions of the debrief:

- The plain form shows every file of the change when the agent stages nothing and makes no new
  file. It "Shows only changes still unstaged". A new file is outside section 4.3: no form of
  `git diff` shows it until you stage it.
- `git diff --exit-code -- tests/` gives 0, so it misses the staged test change. `git diff --exit-code
  HEAD -- tests/` gives 1. The table under "Start wide, then point --exit-code at HEAD for the
  tests.", the row Already staged: "0: missed" and "1: caught".
- The change to `prompts/system.txt` goes into a commit when a directing prompt asks for it, and
  after you score the fields on the evaluation set again. The model reads the system prompt for each
  note, so a change to it can change each reply. The recap of day 3, at the top of today's notebook,
  says: "Score the fields on the evaluation set, on every prompt change".

## Words in the quotes

The quotes keep the words of the notebook. The linter finds nothing in them.
