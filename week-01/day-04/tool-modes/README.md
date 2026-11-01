# Exercise: Map the modes of the coding tool you use

After this exercise, you can say which kind of tool each mode of Codex is, and check what Codex did against a done-when.

**Scenario:** Before the lab's runs, you map the modes of Codex. You try two of them.

**Success criterion:** from `extractor`, `python3 ../check.py` prints `Done:`.

**Where you work:** the folder `~/practice/week-01/day-04/tool-modes/extractor`, and Codex in a terminal. In the Explorer, it is week-01 › day-04 › tool-modes › extractor. Each path starts there.

**Start from:** the lab's saved state `configured`. Run `python3 ~/practice/reset.py tool-modes`. It prints `tool-modes is back as it was supplied`. Run `cd ~/practice/week-01/day-04/tool-modes/extractor`. To start again, run the same reset. It removes Codex's change and your answers.

**What you have:** `modes.md`, which you fill in. Section 4.4, "Which kind of AI coding tool", has the rules.

## Steps

1. Run `code modes.md`. Run `ls -a`. You should see `.claude`, Claude Code's settings, but no `.codex` for Codex.
2. Run `codex`. If it does not start, or asks for a sign-in, tell your trainer.
   1. When Codex asks if you trust this folder, answer yes. The course team wrote each file here, and none holds settings or instructions for Codex. Section 4.4, under "Three kinds of tool, and they need different checks.": "instructions planted in the files such editors read".
   2. Type `/permissions`. Select Read Only. Give this request: `Add this line at the end of README.md: The data-rules check passed before any AI tool ran here.`
   3. See what Codex reads and runs without your yes. If it asks, answer no, or Git can show the line two times.
   4. Type `/permissions`. Select Ask for approval. Give the same request. If it asks, select `Yes, proceed`.
   5. Type `/exit`. Do not commit, so Git shows the change.
   6. Run `git status --short`. Run `git diff HEAD`. It shows the change, staged or not. Section 4.3, figure "The four forms of the command": "Everything since the last commit, staged or not". You should see `M README.md`, and the request's line after `+`.
3. Fill in `modes.md` by hand, as this table gives. Save the file.

| Part of `modes.md` | What to write | Why |
|---|---|---|
| Kind, in each row | `agent` | In `modes.md`, each row says that Codex uses tools without your yes: it reads files and runs commands, in Read Only too. Only an agent does that: chat reaches only what you paste into it. Section 4.4, under "Three kinds of tool, and they need different checks.": "Coding agents: conversational AI models with tools". |
| `Answer:` | `yes` if Git shows only the request's line, at the end of `README.md`. Blank lines do not count. Else `no`. | The done-when in `modes.md` allows only that change. Section 4.4, under the same heading: "then its result against the done-when". |

Run `python3 ../check.py`. You should see `Done:`. If you see `Not yet:`, fix what it names.

**Answer:** `~/practice/week-01/day-04/answers/tool-modes/` holds `modes.md`, `decisions.md`, `codex-run/`, and `commands.sh`, which ends with `Done:`.

## Afterwards, together

- Why does your answer rest on Git, not on Codex's report?
- Which mode will you use for the lab's runs, and what will you check first?
- Which of your files must no agent read, even in Read Only?
