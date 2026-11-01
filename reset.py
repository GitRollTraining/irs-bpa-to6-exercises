"""Put one exercise folder back as it was supplied: python3 reset.py <folder>

The supplied state is the commit tagged `start` (for a day added after you cloned, the latest
commit). Your changes in that folder are replaced, not repaired; no other folder is touched. A
folder whose starting state is a Git repository of its own holds start.py, which this runs to build
that repository again.
"""
import pathlib
import subprocess
import sys

KIT = pathlib.Path(__file__).resolve().parent
# Folders every exercise shares; none of them is an exercise's starting state.
SHARED = {"answers", "notes", "lab-states"}

places = {p.name: p.relative_to(KIT).as_posix() for p in KIT.glob("week-*/day-*/*")
          if p.is_dir() and p.name not in SHARED}
folders = sorted(places)
if len(sys.argv) != 2 or sys.argv[1] not in folders:
    print("Usage: python3 reset.py <folder>, one of: " + ", ".join(folders))
    sys.exit(1)
folder = sys.argv[1]
# A day added after you cloned is not in the commit tagged `start`; its folder comes back as the
# latest commit has it.
in_start = subprocess.run(["git", "-C", str(KIT), "cat-file", "-e", f"start:{places[folder]}"],
                          stderr=subprocess.DEVNULL).returncode == 0
subprocess.run(["git", "-C", str(KIT), "restore", f"--source={'start' if in_start else 'HEAD'}",
                "--staged", "--worktree", "--", places[folder]], check=True)
# Git leaves a folder your terminal is in (it says "Refusing to remove current working
# directory"); start.py then empties it in place.
subprocess.run(["git", "-C", str(KIT), "clean", "-ffdxq", "--", places[folder]], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if (KIT / places[folder] / "start.py").exists():
    subprocess.run([sys.executable, "start.py"], cwd=KIT / places[folder], check=True)
print(f"{folder} is back as it was supplied.")
