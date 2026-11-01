"""The done check for this exercise. From extractor/, run: python3 ../check.py

It reads three repositories through Git: your clone extractor/, the lab's remote shared.git/ and the
repository mirror.git/. It calls no model, starts no agent and needs no network.

It looks for these things:
- origin is the lab's remote, for fetch and for push. docs/remote.md names the lab's remote.
- No push of yours went to a repository that is not the lab's remote.
- The lab's remote still holds your teammate's commit, and it holds your commit.
- Your main holds your teammate's commit, and it is the same commit as the main of the lab's remote.
When ../mirror.git holds a push, only the reset empties it, so the check names the reset alone. When the
lab's remote no longer holds your teammate's commit, only the reset gives it back. Then the check names no
move on your main, which the reset replaces.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CLONE = HERE / "extractor"
SHARED = HERE / "shared.git"
MIRROR = HERE / "mirror.git"
TEAMMATE_REF = "refs/course/teammate"  # set by start.py
# A line that only your commit adds to tests/test_extractor.py.
YOUR_TEST = "def test_reply_with_amount_as_text_is_a_failure"
RESET = "Run python3 ~/practice/reset.py push-after-rejection."
# The notebook's lines that the messages quote, from section 4.2.
BEFORE_PUSH = ('Section 4.2, list "A remote", on git remote -v: "Before the first push, run it: is origin the lab\'s '
               'remote?"')
ORDER = 'Section 4.2, the figure of two copies: "fetch, read what came in, merge, then push."'


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def in_clone(*args):
    return git("-C", str(CLONE), *args)


def bare(folder, *args):
    # --git-dir, so that Git reads a bare repository also where safe.bareRepository is explicit.
    return git("--git-dir", str(folder), *args)


def stop(message):
    print("Not yet: " + message)
    sys.exit(1)


def report(problems):
    """Print each thing left and stop, or print Done."""
    if problems:
        print(f"Not yet: {len(problems)} left.")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    print("Done: origin is the lab's remote, for fetch and for push. The lab's remote holds your teammate's "
          "commit and yours, and your clone matches it.")


def folder_of(url):
    """The folder that a local URL names, as Git reads it from the top of your clone. Git reads ~ as your
    home folder, also in quotes. None when there is no such folder."""
    if url.startswith("file://"):
        url = url[len("file://"):]
    path = pathlib.Path(url).expanduser()
    if not path.is_absolute():
        path = CLONE / path
    for candidate in (path, path.with_name(path.name + ".git")):
        if candidate.is_dir():
            return candidate.resolve()
    return None


def shown(url):
    """A URL as the learner can read it: ../<folder> for a folder beside extractor, else as Git has it."""
    folder = folder_of(url)
    return f"../{folder.name}" if folder and folder.parent == HERE.resolve() else url


def holds_anything(folder):
    """True when a push put a branch or a commit into the repository."""
    if bare(folder, "for-each-ref", "--format=%(refname)").stdout.strip():
        return True
    counts = {}
    for line in bare(folder, "count-objects", "-v").stdout.splitlines():
        name, _, value = line.partition(":")
        counts[name.strip()] = value.strip()
    return any(counts.get(name, "0") not in ("", "0") for name in ("count", "in-pack"))


def main():
    if not (CLONE / ".git").is_dir():
        stop("there is no clone extractor/ yet. " + RESET)
    for folder in (SHARED, MIRROR):
        if bare(folder, "rev-parse", "--is-bare-repository").stdout.strip() != "true":
            stop(f"../{folder.name} is missing. " + RESET)
    teammate = bare(SHARED, "rev-parse", "-q", "--verify", TEAMMATE_REF + "^{commit}").stdout.strip()
    if not teammate:
        stop("../shared.git no longer has the mark of your teammate's commit. " + RESET)
    if holds_anything(MIRROR):
        report(["../mirror.git holds a push of yours, so every later clone of it holds your commit. " + RESET
                + ' Then do the step "Set the push line" before you push. Section 4.2, list "A push": '
                '"So what you push is in every later clone"'])

    problems = []
    fetch_urls = [u.strip() for u in in_clone("remote", "get-url", "--all", "origin").stdout.split("\n") if u.strip()]
    push_urls = [u.strip() for u in in_clone("remote", "get-url", "--push", "--all", "origin").stdout.split("\n")
                 if u.strip()]
    # The push URLs that origin's config holds. With two or more, as set-url --add --push makes, set-url --push fails.
    pushurl_values = in_clone("config", "--get-all", "remote.origin.pushurl").stdout.splitlines()
    wrong_push = [shown(u) for u in push_urls if folder_of(u) != SHARED.resolve()]
    wrong_fetch = [shown(u) for u in fetch_urls if folder_of(u) != SHARED.resolve()]
    if not fetch_urls:
        problems.append("your clone extractor has no remote named origin. " + RESET + ' Then do the steps again, from '
                        '"Check the remote" on. ' + BEFORE_PUSH)
    if wrong_push and len(pushurl_values) > 1:
        problems.append('origin has more than one (push) line, so the command of the step "Set the push line" fails. '
                        "Run git config --unset-all remote.origin.pushurl. Then origin pushes where it fetches from. "
                        + BEFORE_PUSH)
    elif wrong_push:
        problems.append(f"origin pushes to {', '.join(wrong_push)}, not to ../shared.git, the lab's remote that "
                        'docs/remote.md names. The step "Set the push line" gives the command. ' + BEFORE_PUSH)
    if wrong_fetch:
        problems.append(f"origin fetches from {', '.join(wrong_fetch)}, not from ../shared.git, the lab's remote "
                        'that docs/remote.md names. The step "Set the push line" keeps this line. To set it back, run '
                        "git remote set-url origin ~/practice/week-01/day-04/push-after-rejection/shared.git. "
                        + BEFORE_PUSH)

    shared_main = bare(SHARED, "rev-parse", "-q", "--verify", "refs/heads/main").stdout.strip()
    if not shared_main or bare(SHARED, "merge-base", "--is-ancestor", teammate, shared_main).returncode:
        problems.append("../shared.git, the lab's remote, no longer holds your teammate's commit: a push replaced it. "
                        "Git rejects such a push unless you give --force. " + RESET + ' Then do the steps again, '
                        'from "Set the push line" on, with no --force. Section 4.2, the Check\'s answer: "Git will '
                        'not let your push replace commits it has not seen"')
        report(problems)
    mine = in_clone("rev-parse", "-q", "--verify", "refs/heads/main").stdout.strip()
    lacks_teammate = False
    if (CLONE / ".git" / "MERGE_HEAD").exists():
        problems.append("a merge in extractor waits for its commit. Run git commit --no-edit to finish it. The step "
                        '"Merge" gives the merge. ' + ORDER)
    elif not mine or in_clone("merge-base", "--is-ancestor", teammate, mine).returncode:
        lacks_teammate = True
        problems.append("your main in extractor does not hold your teammate's commit yet. Git rejects a push that "
                        'would replace it. The steps "Fetch", "Read what came in" and "Merge" give the commands. '
                        + ORDER)
    pushed = bare(SHARED, "show", "main:tests/test_extractor.py").stdout if shared_main else ""
    if YOUR_TEST not in pushed:
        problems.append('../shared.git, the lab\'s remote, does not hold your commit yet. The step "Push again" '
                        'sends it, after the merge. Section 4.2, list "A push": "Sends your commits to the URL origin '
                        'holds"')
    elif mine != shared_main and not lacks_teammate:
        problems.append("your main in extractor and the main of ../shared.git are not the same commit yet. Run git "
                        'push, as the step "Push again" says. ' + ORDER)
    report(problems)


if __name__ == "__main__":
    main()
