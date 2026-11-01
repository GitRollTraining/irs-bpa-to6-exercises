"""Send notes to the model that the extractor calls, and record each reply for the extractor's tests.
From lab/, run:

    python3 ../record.py 0147 0102 0104

The script sends each note as the extractor sends a note: inside <note> tags, with the output schema,
and with prompts/system.txt as it is now. The lab's model.py sends it. The script keeps each reply in a
folder in runs/. It makes the name of that folder from the prompt and the schema. Then it copies the
replies into tests/recorded/, where the tests read them.

The script sends a note only when its folder in runs/ has no reply for that note. So it sends again
after you change the prompt. With the same prompt, it sends nothing. While prompts/system.txt is still
the draft that the course gave you, it sends nothing.
"""
import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE / "lab"
DRAFT = HERE / "files" / "system.txt"


def fingerprint(prompt, schema):
    """The name of the folder of a run in runs/: made from the system prompt and the schema, as the
    extractor sends them."""
    sent = prompt + "\n\0\n" + json.dumps(schema, sort_keys=True)
    return hashlib.sha256(sent.encode("utf-8")).hexdigest()[:12]


def main(args):
    if not (LAB / ".git").is_dir():
        sys.exit("There is no repository lab/ yet. Run python3 ~/practice/reset.py system-prompt.")
    if not args or not all((LAB / "notes" / f"{note}.txt").is_file() for note in args):
        sys.exit("Usage: python3 ../record.py NOTE ..., with the number of each note, such as 0147. "
                 "The notes are in notes/.")
    sys.path.insert(0, str(LAB))
    import extractor  # the lab's extractor: it reads the prompt and the schema now
    from model import ask  # the lab's copy of the route to the model

    if DRAFT.is_file() and extractor.SYSTEM_PROMPT.split() == DRAFT.read_text().split():
        sys.exit("prompts/system.txt is still the draft, so the script sends nothing. "
                 "Fix the three problems in it first.")
    run = LAB / "runs" / fingerprint(extractor.SYSTEM_PROMPT, extractor.SCHEMA)
    run.mkdir(parents=True, exist_ok=True)
    (run / "prompt.txt").write_text(extractor.SYSTEM_PROMPT)
    to_send = [note for note in args if not (run / f"{note}.json").is_file()]
    for note in args:
        if note not in to_send:
            print(f"Note {note}: a reply to this prompt is already saved. No call.")

    failed = []
    for number, note in enumerate(to_send, start=1):
        replies = []

        def record(system_prompt, note_text, schema=None):
            reply = ask(system_prompt, note_text, schema)
            replies.append(reply)
            return reply

        try:
            extractor.extract((LAB / "notes" / f"{note}.txt").read_text(), ask=record)
            result = ""
        except extractor.ExtractionFailed as failure:
            result = f" The reply fails the extractor's check: {failure}."
        except Exception as failure:  # the route failed, so there is no reply to keep
            failed.append(note)
            print(f"Note {note}: no reply. {failure}", flush=True)
            continue
        (run / f"{note}.json").write_text(replies[0].strip() + "\n")
        print(f"Reply {number} of {len(to_send)} saved: note {note}.{result}", flush=True)

    recorded = LAB / "tests" / "recorded"
    recorded.mkdir(parents=True, exist_ok=True)
    done = []
    for note in args:
        if (run / f"{note}.json").is_file():
            shutil.copy(run / f"{note}.json", recorded / f"{note}.json")
            done.append(f"{note}.json")
            print(f"{note}: " + (run / f"{note}.json").read_text().strip())
    print("Recorded in tests/recorded/: " + (", ".join(done) or "nothing"))
    if failed:
        sys.exit(f"No reply for {', '.join(failed)}. Run the same command again. It sends only the notes that have "
                 "no reply. If it stops a second time, tell your trainer.")


if __name__ == "__main__":
    main(sys.argv[1:])
