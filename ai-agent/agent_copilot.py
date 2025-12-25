#!/usr/bin/env python3

from pathlib import Path
import subprocess
import datetime
import sys
import tempfile
import difflib

# =========================
# CONFIG
# =========================

ROOT = Path("app/src")
ALLOWED_SUFFIXES = (".java", ".kt")
MAX_FILE_SIZE = 50_000          # bytes
MIN_OUTPUT_RATIO = 0.7          # output must be >= 70% of input
BRANCH_PREFIX = "ai/todo-cleanup"
BASE_BRANCH = "master"
DRY_RUN = False                 # set True to disable writes/commits
ONLY_AI_TODO = False            # True => only TODO(ai)

# =========================
# UTILS
# =========================

def sh(cmd: str):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def git_clean():
    result = subprocess.run(
        "git status --porcelain",
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print("❌ Working tree not clean. Commit or stash first.")
        sys.exit(1)

def detect_main_branch():
    for name in ("master", "main"):
        try:
            subprocess.run(
                f"git show-ref --verify --quiet refs/heads/{name}",
                shell=True,
                check=True,
            )
            return name
        except subprocess.CalledProcessError:
            pass
    print("❌ Cannot detect main branch")
    sys.exit(1)

# =========================
# GIT SETUP
# =========================

git_clean()

BASE_BRANCH = detect_main_branch()
print(f"Detected main branch: {BASE_BRANCH}")

branch_name = f"{BRANCH_PREFIX}/{datetime.date.today()}"
print(f"Creating branch: {branch_name}")

sh(f"git fetch origin {BASE_BRANCH}")
sh(f"git checkout {BASE_BRANCH}")
sh(f"git pull origin {BASE_BRANCH}")
sh(f"git checkout -B {branch_name}")

# =========================
# FILE DISCOVERY
# =========================

files = [
    p for p in ROOT.rglob("*")
    if p.suffix in ALLOWED_SUFFIXES
       and "build" not in p.parts
       and "generated" not in p.parts
       and p.is_file()
       and p.stat().st_size < MAX_FILE_SIZE
]

if not files:
    print("No candidate files found.")
    sys.exit(0)

# =========================
# PROCESS FILES
# =========================

changed_files = []

for file in files:
    code = file.read_text(encoding="utf-8", errors="ignore")

    if "TODO" not in code:
        continue

    if ONLY_AI_TODO and "TODO(ai)" not in code:
        continue

    print(f"🧹 Processing {file}")

    prompt = f"""
You are a senior Android developer.

TASK:
- Clean ONLY trivial TODOs
- Do NOT change logic or architecture
- Do NOT add new features
- Return the FULL file content
- If TODO cannot be safely resolved, return the file unchanged

FILE:
{code}
"""

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    sh(f'copilot -p "{prompt}" > {tmp_path}')

    out = Path(tmp_path).read_text(encoding="utf-8", errors="ignore").strip()

    # =========================
    # SAFETY CHECKS
    # =========================

    if len(out) < len(code) * MIN_OUTPUT_RATIO:
        print("⚠️ Output too short – skipping")
        continue

    if "class " not in out and "interface " not in out:
        print("⚠️ No class/interface detected – skipping")
        continue

    if out.strip() == code.strip():
        print("⏭️ No effective change")
        continue

    # =========================
    # DIFF (optional visibility)
    # =========================

    diff = difflib.unified_diff(
        code.splitlines(),
        out.splitlines(),
        fromfile=str(file),
        tofile=str(file),
        lineterm=""
    )

    print("\n".join(list(diff)[:40]))

    if DRY_RUN:
        print("🧪 DRY RUN – not writing file")
        continue

    file.write_text(out, encoding="utf-8")
    changed_files.append(file)
    print(f"✅ Updated {file}")

# =========================
# COMMIT & PUSH
# =========================

if not changed_files:
    print("Nothing changed. Exiting.")
    sys.exit(0)

if DRY_RUN:
    print("🧪 DRY RUN – skipping commit/push")
    sys.exit(0)

sh("git add .")
sh("git commit -m 'chore(ai): cleanup trivial TODOs'")
sh(f"git push -u origin {branch_name}")

print("\n🎉 AI cleanup completed successfully.")
print(f"➡️ Open PR from {branch_name} into {BASE_BRANCH}")
