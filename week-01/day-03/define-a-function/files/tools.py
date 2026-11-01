"""Your code: the functions that the model can ask for. The model only asks. A call runs here.

Each function in functions.json has its code in this file, by the same name.
"""
import pathlib

LAB = pathlib.Path(__file__).resolve().parent

# The forms that the practice notes name, with the title of each, as the IRS page "About Form ..."
# for it gives the title (https://www.irs.gov/forms-pubs/about-form-5329 and the pages like it).
FORMS = {
    "940": "Employer's Annual Federal Unemployment (FUTA) Tax Return",
    "941": "Employer's Quarterly Federal Tax Return",
    "990": "Return of Organization Exempt from Income Tax",
    "1040": "U.S. Individual Income Tax Return",
    "1041": "U.S. Income Tax Return for Estates and Trusts",
    "1065": "U.S. Return of Partnership Income",
    "1098": "Mortgage Interest Statement",
    "1098-T": "Tuition Statement",
    "1099-DIV": "Dividends and Distributions",
    "1099-G": "Certain Government Payments",
    "1099-INT": "Interest Income",
    "1099-K": "Payment Card and Third Party Network Transactions",
    "1099-NEC": "Nonemployee Compensation",
    "1120": "U.S. Corporation Income Tax Return",
    "1120-S": "U.S. Income Tax Return for an S Corporation",
    "5329": "Additional Taxes on Qualified Plans (including IRAs) and Other Tax-Favored Accounts",
    "8962": "Premium Tax Credit",
    "W-2": "Wage and Tax Statement",
    "W-2G": "Certain Gambling Winnings",
}


def lookup_form(form_number):
    """Give the title of a form, such as "U.S. Individual Income Tax Return" for "1040".

    form_number is the number of the form as text, such as "1040", "1120-S" or "W-2". It has no word
    "Form" in it. For a number that is not in FORMS, the function gives None. It reads FORMS only.
    It writes nothing.
    """
    return FORMS.get(form_number.strip().upper())


def add_follow_up(note_id, text):
    """Add the text as a line to the case file, cases/<note_id>.txt, for the case that the note is about.

    The caseworker of the case reads that file to know what to do next.
    """
    case_file = LAB / "cases" / f"{note_id}.txt"
    case_file.parent.mkdir(exist_ok=True)
    with open(case_file, "a") as out:
        out.write(f"Follow-up: {text}\n")
