#!/usr/bin/env python3
import subprocess
import os
import datetime

def sh(cmd):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

MAIN = "master"
DATE = datetime.datetime.now().strftime("%Y-%m-%d")
BRANCH = f"ai/todo-cleanup/{DATE}"

# 1. branch
sh(f"git checkout {MAIN}")
sh(f"git pull origin {MAIN}")
sh(f"git checkout -B {BRANCH}")

# 2. find files with TODO
files = subprocess.check_output(
    "grep -rl TODO app/src || true",
    shell=True,
    text=True
).splitlines()

for file in files:
    print(f"🧹 Processing {file}")
    sh(f"""
copilot generate \
  -f {file} \
  -p "Clean trivial TODOs. Do not change logic or architecture. Return full file." \
  > /tmp/ai_out.txt
""")

    if os.path.getsize("/tmp/ai_out.txt") > 50:
        sh(f"cp /tmp/ai_out.txt {file}")
    else:
        print("⚠️ Empty output, skipping")

# 3. commit + push
sh("git add .")
sh("git commit -m 'chore(ai): cleanup TODOs' || true")
sh(f"git push origin {BRANCH} --force")

