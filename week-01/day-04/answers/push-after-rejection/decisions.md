# The course's answer: each decision, its reason, and its rule

The check reads three repositories through Git: your clone `extractor`, `../shared.git` and `../mirror.git`. No model and no coding agent made any part of this answer. The rules are in section 4.2 of the day's notebook, "Fetch, pull and push".

| Decision | The answer | Why | The check also accepts |
|---|---|---|---|
| The `(push)` line of `git remote -v` | Set it to the lab's remote: `git remote set-url --push origin ~/practice/week-01/day-04/push-after-rejection/shared.git`. | `docs/remote.md` names `shared.git`, the lab's remote. The `(fetch)` line names it. But `git push` uses the `(push)` line, which names `mirror.git`, not the lab's remote. In the scenario, your coding agent set it. So a push would send your commit to the wrong repository, and every later clone of it would hold your commit. Section 4.2, list "A remote", on `git remote -v`: "Before the first push, run it: is origin the lab's remote?" List "A push": "So what you push is in every later clone". | The same folder in another form: `../shared.git`, which Git reads from the top of `extractor`, or a `file://` address. Or no push line: `git config --unset remote.origin.pushurl`, so that origin pushes to the folder that it fetches from. Or origin removed and added again with the lab's remote. Then the first push is `git push -u origin main`. |
| The `(fetch)` line | Keep it. | It names `shared.git`, the folder that `docs/remote.md` names. The same rule. | Any other form of the same folder. |
| What you do after the rejection | `git fetch`, then `git show --stat origin/main`, then `git merge --no-edit origin/main`, then `git push`. Not the `git pull` that Git's hint names. | A pull also tries to merge what came in, before you read it. A fetch only downloads, so you can read your teammate's commit first. The merge commit holds your teammate's commit and yours, so the next push replaces nothing. Section 4.2, the figure of two copies: "fetch, read what came in, merge, then push." The Check's answer: "Git will not let your push replace commits it has not seen". | `git pull --no-rebase`, a fetch and then a merge: in the table of the three commands, row "git pull": "git fetch, then git merge". `git pull --rebase`, which puts your commit on top of your teammate's commit. Here, a plain `git pull` fetches, then stops with an error and merges nothing. Git 2.50.1 asks for `--no-rebase` or `--rebase` when both sides have new commits. The debrief starts from the answer's order, as a pull tries to merge before you read what came in. |

The check does not accept these:

- A push that went to `../mirror.git`. Then the check names only the reset. Section 4.2, list "A push": "So what you push is in every later clone". Here, the reset takes it back. Out of the course, nothing takes it back.
- A push that replaced your teammate's commit, such as `git push --force`. Then the check names only the reset, which gives the commit back.
- A merge that is not finished. Then the check names `git commit --no-edit`, which finishes it.

## Findings of the linter on the notebook's words

The quotes keep the words of the notebook. `ste-lint.py` finds one thing in them:

- The name that the notebook gives this exercise holds the word `get`. The name is in the source line of the figure of two copies, and in the heading of the exercise. The linter reads each `fetch` in a file with that name as a synonym of `get`, in a quote or not. Git names the command `fetch`.

The steps cut two quotes of the notebook to keep the linter's rules. They call the figure "Two copies of the lab repository push to one remote" the figure of two copies. The rest of its title follows a semicolon. They quote its caption from "fetch" on. The linter reads the words before it as a possible passive voice.
