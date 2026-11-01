# The course's answer: the kind of each mode, and the run in Ask for approval

The course team ran Codex one time for this answer, on 2026-10-30: Codex 0.165.0-alpha.1.2, with the
model GPT-6.1-Sol. The run was in a copy of `~/practice` on a computer of the course team, not in the
hosted workspace. `codex-run/` keeps what Codex showed and the change that it made. `commands.sh`
applies that change.

| Part | The course's answer | Why: the reason, then the notebook line | The check also accepts |
|---|---|---|---|
| Codex's questions, step 2 | Trust this folder: yes. In Read Only: no | The course team wrote each file here, and none holds settings or instructions for Codex: `ls -a` shows `.claude`, Claude Code's settings, and no `.codex`. Section 4.4, under "Three kinds of tool, and they need different checks.", warns of "instructions planted in the files such editors read". A yes in Read Only adds the line, and the run in Ask for approval can add it again. | The check does not read them. Where Git then shows the line two times, the answer is no. |
| Form of `git diff`, step 2 | `HEAD` | Codex can leave its change staged or not, and only `git diff HEAD` shows both. Plain `git diff` misses a staged change, and `git diff --staged`, which section 4.3 runs before every commit, misses an unstaged one. Section 4.3, figure "The four forms of the command", row `git diff HEAD`: "Everything since the last commit, staged or not". | The check does not read it. Plain `git diff` also shows the course's change, as Codex did not stage it. |
| Kind, in each of the four rows | agent | In `modes.md`, each row says that Codex uses tools without your yes: it reads files and runs commands, in Read Only too. Only an agent does that: chat reaches only what you paste into it. Read Only stops edits, not reads and commands, so its name does not change its kind. Section 4.4, under "Three kinds of tool, and they need different checks.": "Coding agents: conversational AI models with tools". In its figure, row Chat, column "What it can reach": "What you paste into it". | Only agent, also with other words, such as "an agent". A kind after "not", "no", "unlike" or "than" is not given: "not an agent" gives no kind. Two kinds in one cell are not accepted. |
| `Answer:` | yes | Git shows only the request's line, at the end of `README.md`. The done-when in `modes.md` allows only that change, and blank lines do not count. Section 4.4, under the same heading: "you check its sandbox, approvals and tool access first, then its result against the done-when." | no, where Git shows another change, such as a new file or the line two times. Yes or no, where the line is at the end in another form, such as in backticks or with no period. For such a line, the debrief starts from no: the done-when names the line as the request gives it. |

The check reads the changes since the start, also a change that you or Codex committed. `modes.md`
is never one of the changes. The check never asks who made a change.

The exercise names Codex only, not Claude Code. Day 4 says so under "Today: Git, as the record of
what the agent did." Its words: "the exercise of section 4.4 uses Codex, the coding tool the hosted
workspace provides".

## What Codex can leave, and what the check says

The first row is the course's run of Codex. The course wrote each of the other rows by hand in
`README.md`, and ran the check on each:

| What Git shows after the run in Ask for approval | The check accepts |
|---|---|
| The line, at the end of `README.md`, with no blank line above it: the course's run | yes |
| The line, at the end of `README.md`, with a blank line above it, and no other change | yes |
| The line at the end, and blank lines added or removed in other places | yes: blank lines do not count |
| The line at the end, in backticks, in quotes or after a list mark | yes or no |
| The line below the heading of `README.md` | no |
| The line joined to the old last line | no |
| The line at the end, and a space added to the old last line | no |
| The line at the end, and new line ends (CRLF) in each line | no |
| The line at the end, and a new file | no |
| The line two times, as after a yes in Read Only too | no |
| The line at the end, in a commit of Codex or of you | yes |
| No change | Not yet: the check asks for the run in Ask for approval |

## Where the facts of each mode come from

- The names of the four modes, and what each does: the list that `/permissions` showed in the
  course's run, in `codex-run/README.md`.
- What Read Only and Ask for approval did without a yes: the course's run, in `codex-run/README.md`.
- The trust question: the course's run did not show it, as the course team set the folder as
  trusted before the run. A trainer sees it in the workspace.
- Approve for me: the page "Permissions", https://learn.chatgpt.com/codex/permission-modes, read on
  2026-10-30: "Approve for me keeps the same workspace-write sandbox as Ask for approval."

The names of the modes can change in a new release of Codex. A trainer runs the exercise one time
in the workspace, and compares what Codex shows there with `codex-run/`.
