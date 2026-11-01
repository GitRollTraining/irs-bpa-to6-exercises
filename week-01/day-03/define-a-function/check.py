"""The done check for this exercise. From lab/, run: python3 ../check.py

It reads functions.json. The list may offer only lookup_form. It tries the schema of lookup_form on three calls.
The first is the call that the question about note 0106 needs. The second has no form_number, and the third has
one more argument. Then it reads the replies that ask.py saved for the function list as it is now, and tests both
questions. For note 0106, the model must ask for one call to lookup_form. The arguments must match the schema, and
your code in tools.py must give the title of Form 5329 for them. For note 0147, the model must ask for no call.

It does not read strict. The course's code that sends your list to the model (model.py) drops strict. So the
check tests each call against the schema in its place. It calls no model. A line for a part of step 2 names
the row of its table that gives the answer. It also quotes the line of the notebook that the answer rests on.
"""
import importlib.util
import itertools
import json
import pathlib
import sys

import jsonschema

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE / "lab"
RESET = "Run python3 ~/practice/reset.py define-a-function."
AGAIN = "Then run python3 ask.py again."
START_AGAIN = "To start again, run python3 ~/practice/reset.py define-a-function, and make the three changes again."
# The two questions that ask.py sends, as it sends them: for note 0106 a call is right, for note 0147 none is.
QUESTIONS = {"call": ("0106", "What is Form 5329, which this note names?"),
             "no-call": ("0147", "What amount is in question?")}
TITLE_5329 = "Additional Taxes on Qualified Plans (including IRAs) and Other Tax-Favored Accounts"
# The kept answer, and what else this check accepts, are in answers/define-a-function/decisions.md.
ALLOWED = "lookup_form"
# The files that the check reads, and where to copy each one from again. A reset gives functions.json again.
SUPPLIED = {"functions.json": None, "tools.py": "../files/tools.py", "system-prompt.txt": "../files/system-prompt.txt",
            "ask.py": "../files/ask.py", "notes/0106.txt": "~/practice/notes/0106.txt",
            "notes/0147.txt": "~/practice/notes/0147.txt"}
# The calls that the check tries the schema of lookup_form on. The third call adds one more argument to the first.
NEEDED = {"form_number": "5329"}
NO_FORM_NUMBER = {}
MORE_NAMES = ("year", "tax_year", "note")
# The lines of section 3.2 that the answers rest on, and what each row of the table in step 2 gives.
BELONGS = 'Section 3.2, the table of functions: "No: that call belongs to a person".'
HARMLESS = 'Section 3.2, the table of functions: "Yes: harmless".'
INTERN = 'Section 3.2, list "Describe each function": "Could an intern use it from that alone?"'
PURPOSE = 'Section 3.2, list "Describe each function": "Its purpose, and each parameter".'
BOTH_KINDS = ('Section 3.2, list "Invented arguments": "Your set: notes where a call is right, and notes where none '
              'is".')
CALLS_ADHERE = 'Section 3.2, list "Describe each function": "strict: true, so calls adhere to the schema".'
BOUNDARY = ('Section 3.2, under "That makes the function list a boundary.": "The model can ask only for what you '
            'defined."')
NOT_NEEDED = 'system-prompt.txt: "Do not call a function that the question does not need."'
ROW_1 = ("functions.json still offers add_follow_up. In tools.py, it writes the next action into the case file. "
         "IRS policy keeps such actions under a person's oversight. Remove it, as row 1 of the table in step 2 says. "
         + BELONGS)
COPY_2 = "Copy the text in row 2 of the table in step 2."
COPY_3 = "Copy the text in row 3 of the table in step 2."
ROW_2 = "The description of lookup_form tells the model when to call it. Use the text in row 2 of the table in step 2."
ROW_3 = "The description of form_number tells the model what to send. Use the text in row 3 of the table in step 2."
# For a list that it sent before, ask.py sends nothing and shows the saved replies. With replies/ removed, it sends.
# A round prints this once: after the quote, at the end of the last line that names row 2 or row 3, before AGAIN.
SEND_AGAIN = ("If the description has that text already, the model can reply differently on each run. To send the "
              "two questions again, run rm -r replies, which removes the saved replies.")
ONLY_LOOKUP = f"After step 2, the list offers only lookup_form. {BOUNDARY}"
SCHEMA_STAYS = f"Step 2 does not change the schema. {CALLS_ADHERE}"
NO_STRICT = "In this lab, model.py drops strict, so a call can break the schema."


def stop(message):
    print("Not yet: 1 left.")
    print("- " + message)
    sys.exit(1)


def undescribed(text):
    return not isinstance(text, str) or not text.strip() or text.strip().upper().startswith("TODO")


def message(case):
    note_id, question = QUESTIONS[case]
    note = (REPO / "notes" / f"{note_id}.txt").read_text().strip()
    return f"<note>{note}</note>\n\nQuestion: {question}"


def saved_reply(case, system_prompt, functions):
    """The reply that ask.py saved for this question with the function list and the system prompt as they
    are now, and its path from lab/. (None, None) when there is none."""
    found = []
    for path in (REPO / "replies").glob(f"*/{case}.json"):
        try:
            record = json.loads(path.read_text())
            sent, reply = record["sent"], record["reply"]
            calls = reply["calls"]
        except (ValueError, KeyError, TypeError):
            continue
        if not isinstance(calls, list) or not all(isinstance(call, dict) for call in calls):
            continue
        if (sent.get("functions"), sent.get("system_prompt"), sent.get("message")) == \
                (functions, system_prompt, message(case)):
            found.append((path.stat().st_mtime, path, reply))
    if not found:
        return None, None
    _, path, reply = max(found, key=lambda item: item[0])
    return path.relative_to(REPO).as_posix(), reply


def load_tools():
    spec = importlib.util.spec_from_file_location("lab_tools", REPO / "tools.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def schema_problems(schema):
    """The problems in the input_schema of lookup_form, and its validator when it can run. Step 2 does not
    change the schema: these lines come only when an edit broke it."""
    if not isinstance(schema, dict) or schema.get("type") != "object" or not isinstance(schema.get("properties"), dict):
        return ['the input_schema of lookup_form must stay as the teammate wrote it: "type": "object", with '
                f'form_number in "properties". {SCHEMA_STAYS}'], None
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as failure:
        return [f"the input_schema of lookup_form is not a valid JSON Schema. jsonschema reports: "
                f"{failure.message.rstrip('.')}. {SCHEMA_STAYS}"], None
    problems = []
    properties = schema["properties"]
    form_number = properties.get("form_number")
    text = form_number.get("description") if isinstance(form_number, dict) else None
    if "form_number" not in properties:
        problems.append(f"the input_schema of lookup_form has no form_number. lookup_form in tools.py takes it. "
                        f"{SCHEMA_STAYS}")
    elif undescribed(text):
        problems.append(f"the description of form_number, in functions.json, {no_text(text)}. tools.py finds the title "
                        f"of 5329, but nothing for Form 5329. {COPY_3} {PURPOSE}")
    others = sorted(set(properties) - {"form_number"})
    if others:
        problems.append("the input_schema of lookup_form has an argument that lookup_form in tools.py does not take: "
                        + ", ".join(others) + f". {SCHEMA_STAYS}")
    validator = jsonschema.Draft202012Validator(schema)
    if not validator.is_valid(NEEDED):
        problems.append(f"the input_schema of lookup_form does not accept {json.dumps(NEEDED)}, the call that the "
                        f"question about note 0106 needs. {SCHEMA_STAYS}")
    accepts = []
    if validator.is_valid(NO_FORM_NUMBER):
        accepts.append("a call with no form_number")
    extra = next(name for name in itertools.chain(MORE_NAMES, (f"extra_{n}" for n in itertools.count(1)))
                 if name not in properties)
    if validator.is_valid({**NEEDED, extra: "2023"}):
        accepts.append(f'a call with one more argument, such as "{extra}"')
    if accepts:
        problems.append("the input_schema of lookup_form accepts " + ", and ".join(accepts) + '. Keep "required": '
                        '["form_number"] and "additionalProperties": false, as the teammate wrote them. '
                        f"{CALLS_ADHERE}")
    return problems, validator


def when_to_call(path, case, names=("lookup_form",)):
    """The line for a reply that calls where none is right, or calls not where one is."""
    if case == "call":
        what = (f"for note 0106, the model asks for no call ({path}). Its question asks what Form 5329 is, and the "
                "note does not say it. So a call is right.")
    else:
        what = (f"for note 0147, the model asks for a call to {' and '.join(names)} ({path}). Its question asks for an "
                "amount, which the note gives. So no call is right.")
    # A call to a function that step 2 removes is fixed by row 1. A call to lookup_form is fixed by its description.
    # Each fix quotes one line of section 3.2.
    fix = f"{ROW_2} {BOTH_KINDS}" if set(names) == {ALLOWED} else ONLY_LOOKUP
    return f"{what} {fix} {AGAIN}"


def no_text(text):
    """How a description that is not written yet reads in a line of the check."""
    if not isinstance(text, str) or not text.strip().upper().startswith("TODO"):
        return "has no text"
    return "is still TODO" if text.strip().upper() == "TODO" else "still starts with TODO. Remove the word TODO"


def call_problems(path, reply, validator, tools):
    """The problems in the reply for note 0106, where one call to lookup_form is right."""
    calls = reply["calls"]
    if not calls:
        return [when_to_call(path, "call")]
    if len(calls) > 1:
        return [f"for note 0106, the model asks for {len(calls)} calls ({path}). The question is about one form, so "
                f"one call is right. {NOT_NEEDED} {ROW_2} {INTERN} {AGAIN}"]
    name, arguments = calls[0].get("name"), calls[0].get("arguments")
    if name != ALLOWED:
        return [f"for note 0106, the model asks for {name}, not lookup_form ({path}). {ONLY_LOOKUP} {AGAIN}"]
    if validator is not None and not validator.is_valid(arguments):
        return [f"for note 0106, the arguments {json.dumps(arguments)} do not match the input_schema of lookup_form "
                f"({path}). {NO_STRICT} {ROW_3} {CALLS_ADHERE} {AGAIN}"]
    try:
        title = tools.lookup_form(**arguments)
    except Exception:  # a call that your code cannot run gives no title
        title = None
    if title != TITLE_5329:
        return [f"for note 0106, the model asks for lookup_form with {json.dumps(arguments)}, and tools.py gives no "
                f"title of Form 5329 for it ({path}). tools.py finds the title of 5329, but nothing for Form 5329. "
                f"{ROW_3} {PURPOSE} {AGAIN}"]
    return []


if not (REPO / ".git").is_dir():
    stop("there is no repository lab yet. " + RESET)
for needed, source in SUPPLIED.items():
    if not (REPO / needed).exists():
        if source is None:
            stop(f"{needed} is missing. {RESET} The reset gives you the file again.")
        stop(f"{needed} is missing. To get it again, run cp {source} {needed}.")
try:
    functions = json.loads((REPO / "functions.json").read_text())
except json.JSONDecodeError as err:
    stop(f"functions.json is not valid JSON. Python reports: {err.msg} (line {err.lineno}). Near that line, look for "
         "a comma, or for a quote inside a text with no \\ before it. The table in step 2 gives each text as "
         f"functions.json needs it. {START_AGAIN}")
if not isinstance(functions, list) or not all(isinstance(f, dict) and isinstance(f.get("name"), str)
                                              for f in functions):
    stop("functions.json must hold a list of function definitions, each with a name, as the teammate wrote it.")
try:
    tools = load_tools()
except Exception as failure:  # the check reports an edit that stops tools.py loading, and goes on
    stop(f"tools.py does not load. Python reports {type(failure).__name__}: {failure}.")

problems = []
offered = {}
for definition in functions:
    if definition["name"] in offered:
        problems.append(f"functions.json offers {definition['name']} two times. Keep one definition of it.")
    offered[definition["name"]] = definition
for name in offered:
    if not callable(getattr(tools, name, None)):
        problems.append(f"functions.json offers {name}, which tools.py does not have. Your code can run only a "
                        f"function in tools.py. {ONLY_LOOKUP}")
    elif name == "add_follow_up":
        problems.append(ROW_1)
    elif name != ALLOWED:
        problems.append(f"functions.json offers {name}. The two questions need only lookup_form. {ONLY_LOOKUP}")

validator = None
lookup = offered.get(ALLOWED)
if lookup is None:
    problems.append("functions.json does not offer lookup_form. The question about note 0106 needs it. Step 2 keeps "
                    f"it, and writes its two descriptions. {HARMLESS} {START_AGAIN}")
else:
    if undescribed(lookup.get("description")):
        problems.append(f"the description of lookup_form, in functions.json, {no_text(lookup.get('description'))}. The "
                        f"model reads it to know when to call the function. {COPY_2} {INTERN}")
    found, validator = schema_problems(lookup.get("input_schema"))
    problems += found

system_prompt = (REPO / "system-prompt.txt").read_text()
replies = {case: saved_reply(case, system_prompt, functions) for case in QUESTIONS}
missing = [QUESTIONS[case][0] for case, (path, reply) in replies.items() if reply is None]
if missing:
    problems.append(f"ask.py saved no reply for the question about note {' or note '.join(missing)} with "
                    "functions.json as it is now. The two replies test your list. When the list is ready, run "
                    f"python3 ask.py, as step 2 says. {BOTH_KINDS}")
if replies["call"][1] is not None and lookup is not None:
    problems += call_problems(*replies["call"], validator, tools)
path, reply = replies["no-call"]
if reply is not None and reply["calls"]:
    problems.append(when_to_call(path, "no-call", sorted({str(call.get("name")) for call in reply["calls"]})))

if problems:
    rows = [n for n, p in enumerate(problems) if ROW_2 in p or ROW_3 in p]
    if rows:
        last = problems[rows[-1]]
        problems[rows[-1]] = (last[:-len(AGAIN)] + f"{SEND_AGAIN} {AGAIN}" if last.endswith(AGAIN)
                              else f"{last} {SEND_AGAIN}")
    print(f"Not yet: {len(problems)} left.")
    print("\n".join(f"- {p}" for p in problems))
    sys.exit(1)
arguments = json.dumps(replies["call"][1]["calls"][0]["arguments"])
print(f"Done: the list offers only lookup_form, with both descriptions. For note 0106, the model asks for lookup_form "
      f"with {arguments}. For note 0147, it asks for no call.")
