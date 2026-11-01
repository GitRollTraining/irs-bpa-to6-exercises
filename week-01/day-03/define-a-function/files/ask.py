"""Send two questions about case notes to the model, with the function list in functions.json:

    python3 ask.py

For each question, the model gets system-prompt.txt, the note, the question and the function list.
It can answer in text, or ask for a call to a function on the list. ask.py saves each reply in
replies/, in a folder for the function list as it is now. Then it shows each reply. For a call to
lookup_form, it runs the call in your code, tools.py, and shows what lookup_form gives. It runs no
other function.

ask.py sends a question only when replies/ holds no reply to it for the function list as it is now. So
after each change to functions.json, it sends the two questions again: two calls to the model. It
sends nothing while a function or a parameter on the list has no description, or one that still
starts with TODO.
"""
import hashlib
import json
import pathlib
import sys

LAB = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import tools  # noqa: E402  your code, which runs each call
from model import ask  # noqa: E402  the course's code that sends a question to the model

# The two questions. For the first, a call is right. For the second, no call is right.
QUESTIONS = [
    {"case": "call", "note": "0106", "question": "What is Form 5329, which this note names?"},
    {"case": "no-call", "note": "0147", "question": "What amount is in question?"},
]


def message(question):
    note = (LAB / "notes" / f"{question['note']}.txt").read_text().strip()
    return f"<note>{note}</note>\n\nQuestion: {question['question']}"


def undescribed(text):
    """True for a description that is not there yet: empty, or only TODO."""
    return not isinstance(text, str) or text.strip().upper() in ("", "TODO")


def function_list():
    """The function list from functions.json. It stops with the reason when the list cannot go to the model."""
    try:
        functions = json.loads((LAB / "functions.json").read_text())
    except json.JSONDecodeError as err:
        sys.exit(f"Not sent: functions.json is not valid JSON. Python reports: {err.msg} (line {err.lineno}). "
                 "Near that line, look for a comma, or for a quote inside a text with no \\ before it.")
    if not isinstance(functions, list) or not all(isinstance(f, dict) for f in functions):
        sys.exit("Not sent: functions.json must hold a list of function definitions, as the teammate wrote it.")
    missing, todo = [], []
    for f in functions:
        name = f.get("name") or "a function with no name"
        if not isinstance(f.get("input_schema"), dict):
            sys.exit(f"Not sent: {name} has no input_schema in functions.json.")
        texts = [(name, f.get("description"))] + [
            (f"{parameter} in {name}", rule.get("description") if isinstance(rule, dict) else None)
            for parameter, rule in (f["input_schema"].get("properties") or {}).items()]
        for what, text in texts:
            if undescribed(text):
                missing.append(what)
            elif text.strip().upper().startswith("TODO"):
                todo.append(what)
    # A description with more text after TODO has its text: it is named apart, in the words of the check.
    reasons = ([f"These have no description yet: {', '.join(missing)}."] if missing else []) \
        + [f"The description of {what} still starts with TODO." for what in todo] \
        + (["Remove the word TODO."] if todo else [])
    if reasons:
        said = " ".join(reasons)
        sys.exit(f"Not sent: {said[0].lower()}{said[1:]} The model reads the descriptions to know what each "
                 "function does.")
    return functions


def fingerprint(system_prompt, functions):
    """A name for what ask.py sends: the system prompt, the function list and the two messages."""
    sent = {"system_prompt": system_prompt, "functions": functions, "messages": [message(q) for q in QUESTIONS]}
    return hashlib.sha256(json.dumps(sent, sort_keys=True).encode()).hexdigest()[:12]


def one_line(text, most=300):
    text = " ".join(str(text).split())
    return text if len(text) <= most else text[:most] + " ..."


def show(number, question, reply):
    print(f"Question {number}, about note {question['note']}: {question['question']}")
    if not reply["calls"]:
        print(f"  The model asks for no call. It answers: {one_line(reply['text'])}")
    for call in reply["calls"]:
        print(f"  The model asks for a call: {call['name']} with {json.dumps(call['arguments'])}")
        if call["name"] != "lookup_form":
            print(f"  ask.py runs only lookup_form. It does not run {call['name']}.")
            continue
        try:
            title = tools.lookup_form(**call["arguments"])
        except Exception as failure:  # ask.py shows a call that your code cannot run, and goes on
            print(f"  Your code cannot run this call. Python reports {type(failure).__name__}: {failure}")
            continue
        if title is None:
            print("  Your code runs it. lookup_form finds no form with that number, and gives None.")
        else:
            print(f"  Your code runs it. lookup_form gives: {title}")
    print()


def main():
    system_prompt = (LAB / "system-prompt.txt").read_text()
    functions = function_list()
    folder = LAB / "replies" / fingerprint(system_prompt, functions)
    to_send = [q for q in QUESTIONS if not (folder / f"{q['case']}.json").exists()]
    if not to_send:
        print("The replies for the function list as it is now are in replies/ already. ask.py sends nothing.")
    folder.mkdir(parents=True, exist_ok=True)
    for number, question in enumerate(to_send, 1):
        try:
            reply = json.loads(ask(system_prompt, message(question), functions=functions))
        except Exception as failure:  # no reply came back: ask.py says so, and keeps the replies that it saved
            sys.exit(f"The model did not reply. model.py reports: {failure}\n"
                     "Run python3 ~/practice/check_setup.py. If it prints Missing, tell your trainer.")
        record = {"case": question["case"], "note": question["note"], "question": question["question"],
                  "sent": {"system_prompt": system_prompt, "functions": functions, "message": message(question)},
                  "reply": reply}
        (folder / f"{question['case']}.json").write_text(json.dumps(record, indent=2) + "\n")
        print(f"Reply {number} of {len(to_send)} saved.")
    print()
    for number, question in enumerate(QUESTIONS, 1):
        show(number, question, json.loads((folder / f"{question['case']}.json").read_text())["reply"])


if __name__ == "__main__":
    main()
