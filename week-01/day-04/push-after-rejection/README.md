# Exercise: Check the remote, push, get rejected, and push again

After this exercise, you can check where a push goes, and push again after a rejection without losing your teammate's work.

**Scenario:** You committed a coding agent's change, and the agent set where your clone pushes. Then a teammate pushed to the lab's remote. Push your commit there, and keep your teammate's work.

**Success criterion:** from `extractor`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-04/push-after-rejection/extractor`, with Git. In the Explorer, it is week-01 › day-04 › push-after-rejection › extractor. Each path in this exercise starts there. Do not use AI tools.

**Start from:** your clone `extractor`, after your teammate's push. Run `python3 ~/practice/reset.py push-after-rejection`. It prints `push-after-rejection is back as it was supplied.` Then run `cd ~/practice/week-01/day-04/push-after-rejection/extractor`. To start again, run the same reset. It removes your commits and your pushes.

**What you have:** `docs/remote.md` names the lab's remote. Each `.git` folder beside `extractor` takes the place of a repository on a Git host. `../check.py` is the check. The rules are in section 4.2, "Fetch, pull and push".

## Steps

1. Run `git show --stat HEAD`. You should see your commit. If the output fills the screen, press `q`. Then run `code docs/remote.md`.
2. Run the commands under this table in order.

| Step | The answer | Why |
|---|---|---|
| Set the push line | The `(push)` line only | `docs/remote.md` names `shared.git`, the lab's remote. The `(fetch)` line names it. But `git push` uses the `(push)` line, which names `mirror.git`, not the lab's remote. Section 4.2, list "A remote", on `git remote -v`: "Before the first push, run it: is origin the lab's remote?" |
| Fetch | `git fetch`, not the `git pull` that Git's hint names | A pull also tries to merge what came in, before you read it. A fetch only downloads, so you can read it first. Section 4.2, the figure of two copies: "fetch, read what came in, merge, then push." |

   - Check the remote: `git remote -v`. You should see a `(fetch)` and a `(push)` line.
   - Set the push line: `git remote set-url --push origin ~/practice/week-01/day-04/push-after-rejection/shared.git`. `--push` changes only the `(push)` line. Run `git remote -v` again: both lines name `shared.git`.
   - Push: `git push`. You should see `! [rejected]`: your clone does not hold your teammate's commit. If you do not see `rejected`, run the check.
   - Fetch: `git fetch`. You should see `-> origin/main`, your copy of origin's main branch.
   - Read what came in: `git show --stat origin/main`. You should see `Author: Teammate` and two changed files.
   - Merge: `git merge --no-edit origin/main`. `--no-edit` keeps Git's own message, so no editor opens. You should see `Merge made by`.
   - Push again: `git push`. You should see `main -> main`, with no `rejected`.

3. Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names. Then run the check again.

**Answer:** `~/practice/week-01/day-04/answers/push-after-rejection/` holds `decisions.md` and `commands.sh`.

## Afterwards, together

- When should the `(fetch)` and `(push)` lines name two repositories?
- When would `git pull` do as well as a fetch, a read and a merge?
- What in your teammate's commit would make you stop before the merge?
