# The course's run of Codex

The course team did the steps with Codex one time, on 2026-10-30. This folder keeps what Codex
changed and what it showed. The blocks below are lines from the screen of Codex. Some lines are not
in them: lines with a path of the computer, and lines such as "+ Show details". A line that the
screen broke in two is one line here.

- Agent: Codex, the command-line program `codex`, version 0.165.0-alpha.1.2.
- Model: GPT-6.1-Sol, with reasoning medium, as `/status` showed it.
- Date: 2026-10-30.
- Where: in a copy of `~/practice` on a computer of the course team. It was not the hosted workspace
  of the course.
- Settings: the Codex settings of the course team. Before the start, the course team set the folder
  as trusted, so Codex asked no trust question. The course team set the reasoning level to medium.

`ask-for-approval.diff` is the change of Codex in Ask for approval, as `git diff HEAD` showed it.
`../commands.sh` applies it with `git apply`. Then the check reads it as it reads the change of your
run.

## At the start

`/status` showed this line. It shows the sandbox, then the approvals:

```text
Permissions:         Workspace (Ask for approval)
```

`/permissions` showed this list:

```text
› 1. Ask for approval (current)  Read and edit workspace files and run commands, with approval required for internet access or edits outside the workspace
  2. Approve for me              Only ask for actions detected as potentially unsafe
  3. Full Access                 Use with caution: Codex can edit files outside this workspace and access the internet without approval
  4. Read Only                   Read workspace files, with approval required for edits or internet access
```

## The run in Read Only

The course team selected Read Only, the last item. Then `/status` showed this line. The sandbox
changed, and the approvals did not change:

```text
Permissions:         Read Only (Ask for approval)
```

Codex ran two commands without a yes: `pwd && rg --files -g AGENTS.md -g README.md`, and
`cat README.md`. It showed them so:

```text
• I’ll check README.md and append the line you provided.

• Ran pwd && rg --files -g AGENTS.md -g README.md

• Explored
  └ Read README.md
```

Then it asked this question:

```text
Would you like to run the following command?

Environment: local

Reason: The workspace is read-only. Allow appending your requested line to README.md?

$ printf '%s\n' 'The data-rules check passed before any AI tool ran here.' >> README.md

› 1. Yes, proceed (y)
  2. Yes, and don't ask again for commands that start with `printf '%s\n' 'The data-rules check passed before any AI tool ran here.' >> README.md` (p)
  3. No, and tell Codex what to do differently (esc)

Press enter to confirm or esc to cancel
```

The course team selected 3. Codex did not run the command, and `README.md` did not change. Codex
showed "You canceled the request to run printf", and then these lines:

```text
• Exited (status 1) printf '%s\n' 'The data-rules check passed before any AI tool ran here.' >> README.md
  └ (no output)

■ Conversation interrupted - use /feedback if something went wrong
```

The line "Exited (status 1)" does not show a command that ran. Git showed no change.

## The run in Ask for approval

The course team typed `/permissions` and selected Ask for approval, the first item. Then the course
team gave the same request. Codex asked no question. It showed this:

```text
• I’ll append the exact line to README.md and verify it appears once.

• Explored
  └ Read README.md

• Edited README.md (+1 -0)
    13 +The data-rules check passed before any AI tool ran here.

• Explored
  └ Read README.md

• Added the exact line at the end of README.md.
```

Its last report: "Added the exact line at the end of `README.md`." Codex added no blank line above
the line. After `/exit`, Codex showed:

```text
Token usage: total=10,442 input=10,004 (+ 110,848 cached) output=438 (reasoning 14)
```
