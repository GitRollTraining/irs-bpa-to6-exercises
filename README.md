# Practice exercises: the case-notes extractor

This repository holds the practice exercises of the course, by week and by day. Each day has one notebook, with the reading of the day and its exercises in the order of the slides. Each exercise has a folder with its starting files. Its answer is in the folder `answers` of its day.

The course made up every note and name in this repository. Some replies are the model's, and some runs are a coding agent's. A file beside each one says so. The course made up the other replies and runs. None is about a real person, business or tax return.

## Set up once

In the hosted workspace of the course, the folder `~/practice` is this repository. Start at step 3.

On your own computer, do all the steps.

1. Clone the repository into `~/practice`. Then mark the state that a reset restores:

   ```
   git clone https://github.com/GitRollTraining/irs-bpa-to6-2026-11-02-exercises.git ~/practice
   cd ~/practice
   git tag start
   ```

2. Make a Python environment for the exercises, with Python 3.9 or later:

   ```
   python3 -m venv .venv
   .venv/bin/pip install pytest jsonschema ipykernel
   ```

   In each new terminal, run `source ~/practice/.venv/bin/activate` first. Then `python3` has pytest and jsonschema.

3. Give Git your name and email. Git writes them into each commit that you make:

   ```
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```

4. Open the folder `~/practice` in VS Code. If VS Code asks if you trust the authors of the files, select Trust. When VS Code asks for the Python and Jupyter extensions, install them.

5. Open the notebook of the day, such as `week-01/day-01/week-01-day-01.ipynb`. At the top right, select Select Kernel. On your own computer, select the environment `.venv`. In the hosted workspace, select its Python.

## The days

| Day | The notebook | The exercises |
|---|---|---|
| Week 1, day 1 | [`week-01-day-01.ipynb`](week-01/day-01/week-01-day-01.ipynb) | [Three exercises](week-01/day-01/README.md) |
| Week 1, day 2 | [`week-01-day-02.ipynb`](week-01/day-02/week-01-day-02.ipynb) | [Three exercises](week-01/day-02/README.md) |
| Week 1, day 3 | [`week-01-day-03.ipynb`](week-01/day-03/week-01-day-03.ipynb) | [Three exercises](week-01/day-03/README.md) |
| Week 1, day 4 | [`week-01-day-04.ipynb`](week-01/day-04/week-01-day-04.ipynb) | [Four exercises](week-01/day-04/README.md) |
| Week 1, day 5 | [`week-01-day-05.ipynb`](week-01/day-05/week-01-day-05.ipynb) | [Two exercises](week-01/day-05/README.md) |

## The model and your coding agent

**The model.** Four exercises send text to the model that the extractor calls: `same-note-five-times` and `system-prompt` on day 2, and `define-a-function` and `score-the-prompt` on day 3. They send it through `model.py`. The table under "Start an exercise again" says how many calls each one makes after a reset. When you send the same text again, nothing goes to the model. No check calls the model. If a call fails, the script that sends tells you what to do.

**Your coding agent.** Two exercises start a coding agent in a terminal: `tool-modes` on day 4, with Codex, and `direct-run-one` on day 5, with Codex or Claude Code. The other exercises use no coding agent.

1. Open a terminal. In VS Code, select Terminal > New Terminal.
2. Go to the folder that the exercise names.
3. Start the agent: type `codex` for Codex, or `claude` for Claude Code.
4. The first time in a folder, the agent asks if you trust the folder. Answer yes for a folder that the course gave you. Then the agent uses the settings in that folder. Without the yes, Claude Code ignores the list of actions that the folder allows, and Codex can start in Read Only.
5. Before the agent does an action that its settings do not allow, it asks you. Read each question before you answer it.
6. In Codex, type `/status`. Its line `Permissions:` shows the sandbox, then the approvals. In a folder that you trust, it should show `Workspace (Ask for approval)`. `/permissions` lists the modes.
7. Type `/exit` to close the agent.

In the folder, Codex reads `.codex/config.toml`, and Claude Code reads `.claude/settings.json`. In your home folder, Codex keeps `~/.codex/`, and Claude Code keeps `~/.claude/` and `~/.claude.json`. Codex writes your answer to the trust question in `~/.codex/config.toml`. Claude Code writes it in `~/.claude.json`. A reset does not change your home folder.

## Start an exercise again

Run `python3 ~/practice/reset.py <folder>`, such as `python3 ~/practice/reset.py find-note-leaks`. The reset puts the folder of that exercise back as the course supplied it, and builds its Git repository again. It removes your changes and your commits in that folder. It does not change other folders or the answers. In a notebook, the first cell of each exercise runs the reset only when the exercise has no Git repository yet.

| Day | Folder | What its reset builds |
|---|---|---|
| Week 1, day 1 | `find-note-leaks` | `extractor/`: the extractor that the course team committed, and the change of a teammate's coding agent on its own branch. |
| Week 1, day 1 | `data-rules-check` | `lab/`: the lab at its first saved state, the four uses to classify in `docs/data-rules-check.md`, and an exported note that Git ignores. |
| Week 1, day 1 | `agent-boundary` | `lab/`: the lab after its run 2, the facts of the pilot, and a teammate's commit of the settings of the coding agents. |
| Week 1, day 2 | `same-note-five-times` | `lab/`, with `prompt.txt`, `send_five.py` and `record.md`, your record with its rows empty. The saved replies go, so your next send calls the model 10 times. |
| Week 1, day 2 | `system-prompt` | `lab/`: the lab after the data-rules check, with a draft system prompt. The saved replies in `runs/` go, so your next record of a changed prompt calls the model 3 times. |
| Week 1, day 2 | `model-and-reasoning-level` | `lab/`: the lab after its run 2, with `docs/model-scores.md`, `docs/next-tasks.md` and `docs/pull-request.md`. |
| Week 1, day 3 | `validate-replies` | `lab/`: the lab after its run 2, eight saved replies, `count_failures.py`, and a teammate's commit on the branch `fewer-failures`. |
| Week 1, day 3 | `define-a-function` | `lab/`: the lab after the data-rules check, with a teammate's `functions.json`, `tools.py`, `ask.py` and `system-prompt.txt`. The saved replies go, so your next send of a changed list calls the model 2 times. |
| Week 1, day 3 | `score-the-prompt` | `extractor/`: the lab after its run 2, a set of 20 labelled notes, a teammate's change to the prompt, and the first score of the set. Your runs go, so your next score of a changed prompt calls the model 20 times. |
| Week 1, day 4 | `commit-three-of-four` | `extractor/`: the lab after its run 2, a coding agent's changes to four files, not committed, and the log of its run. |
| Week 1, day 4 | `push-after-rejection` | `extractor/`, your clone of the lab with one commit of yours, and two repositories next to it. Then the reset makes a teammate's push. |
| Week 1, day 4 | `diff-views` | `lab/`: the lab after its run 2, and one more run of the coding agent, not committed. |
| Week 1, day 4 | `tool-modes` | `extractor/`, and `modes.md`, your table. Codex's changes go. The settings of Codex in your home folder stay. |
| Week 1, day 5 | `directing-prompt` | `lab/`: the lab after run 1, and `run2-prompt.txt` with the Goal and three empty parts. |
| Week 1, day 5 | `direct-run-one` | `lab/`: the lab before run 1, `run1-prompt.txt`, and `run-1-record.md`, your report with empty parts. The files of your agent's run go. |

## Answers

The answer to each exercise is in `answers/<folder>/`, in the folder of its day. The exercises are not graded, so you can open the answers. Do the exercise first.

## The other files

- `reset.py` puts an exercise back as the course supplied it.
- `notes/` holds the simulated case notes that the exercises share.
- `lab-states/` holds the files of the lab of the week at each of its saved states. The exercises build their starting repositories from it.
- `model.py` and `model-route.json` send a request to the model that the extractor calls. Four exercises of days 2 and 3 use them (see "The model and your coding agent"). No check calls the model.
- `check_setup.py` checks a workspace: Python, pytest, jsonschema, Git, and the model. Outside the hosted workspace, it can show the model as missing.

## Not known yet

Only the hosting team or a trainer can answer these questions. When the course has an answer, the answer replaces its row.

| Question | Who answers | Our proposed answer |
|---|---|---|
| In the hosted workspace, does `claude -p` reach the model, from a terminal and from a notebook cell? With which account? `model.py` sends each call this way. | The hosting team | Yes, each learner's, with Claude Code signed in, as `model-route.json` sets it ([Claude Code headless mode](https://code.claude.com/docs/en/headless)). |
| Is Claude Code, `claude`, in the terminal of the hosted workspace? `direct-run-one` can start it. | The hosting team | Yes, with the sign-in of the row above. If it is not, use Codex for `direct-run-one`. |
| Is `codex`, the command-line tool of Codex, in the terminal of the hosted workspace, and is it signed in? | The hosting team | Yes, as the course's page "Use your coding agent" starts `codex` in a terminal. |
| In the hosted workspace, does Codex ask if you trust the folder? After the yes, does `/status` show `Workspace (Ask for approval)`? | The hosting team | Yes, as Codex's page [Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security) gives for a folder under version control: workspace write, approval on request. |
| Does `code` open a file from a notebook cell? | The hosting team | Not known. If it does not, open the file in the Explorer of VS Code. |
| Is Git 2.28 or later in the hosted workspace? | The hosting team | Yes. `check_setup.py` checks it. |
| In the hosted workspace, is `~/practice` this repository, with the tag `start`? Does the Python of the notebooks have pytest and jsonschema? | The hosting team | Yes, as steps 1 and 2 of "Set up once" make them on your own computer. `check_setup.py` checks pytest and jsonschema. |
| How many coding-agent sessions can one exercise start? | The hosting team | One for each run. `direct-run-one` starts one, and one more for each run that does not meet its done-when. |
| A step says "tell your trainer". How do you tell your trainer? | The trainers | Not known. |
