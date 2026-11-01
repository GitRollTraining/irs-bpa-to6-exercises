# Run 1, by each coding agent

The course gave the four parts of run 1's prompt, on four lines, to Codex one time and to Claude
Code two times, on 2026-10-30. Each run started in `lab/` of a new copy of this repository, as the
reset builds it. The course made the runs on a computer of the course team, not in the hosted
workspace.

| Folder | Agent | Version | Model | The files of the run |
|---|---|---|---|---|
| `codex/` | Codex | codex-cli 0.165.0-alpha.1.2 | gpt-6.1-sol, not shown by the run | `schema/case_notes.schema.json`, `tests/test_schema.py` |
| `claude-code/` | Claude Code | 2.1.314 | claude-opus-5-5 | `schema/extraction.schema.json`, `tests/test_schema.py` |

Each folder holds the files of its run, at their paths in `lab/`. The agents changed no other file.
`codex-report.md` and `claude-code-report.md` hold the last report of each agent, as it came back.

The output of Codex does not name its model. The run did not read a model setting. The list of
models for the account starts with gpt-6.1-sol.

No run set a reasoning level, so each agent used its default level. The course did not give Codex
`-c model_reasoning_effort=<level>`, and did not give Claude Code `--effort <level>`. The output of
each run does not name its level.

The first Claude Code run started in a folder that nobody trusted, so Claude Code did not use the
allow list of the lab. It could not run its tests, and its report said so. The answer keeps the
second run, which got the six rules of that list on its command line. A yes to the trust question
gives the same six rules.

`../commands.sh` copies the files of the Codex run into `lab/`. `../run-1-record.md` is the report
on that run.

Your run can give other names, more files and another number of tests. The check reads the run that
is in `lab/`, so it accepts such a run too. `../decisions.md` says how.
