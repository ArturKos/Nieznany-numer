#!/usr/bin/env python3
import subprocess
import datetime
import os
import sys
import requests

# -------------------- Helper --------------------
def sh(cmd):
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def get_main_branch():
    # detect main branch
    result = subprocess.run(
        "git symbolic-ref refs/remotes/origin/HEAD",
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip().split('/')[-1]
    # fallback
    for b in ["main", "master"]:
        check = subprocess.run(f"git rev-parse --verify {b}", shell=True)
        if check.returncode == 0:
            return b
    print("Cannot detect main branch. Exiting.")
    sys.exit(1)

def find_todo_files(root="app/src"):
    todo_files = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith((".kt", ".java")):
                path = os.path.join(dirpath, f)
                with open(path, "r", encoding="utf-8") as file:
                    if "TODO" in file.read():
                        todo_files.append(path)
    return todo_files

def run_ai_on_file(file_path, rules_path="ai-agent/rules.md", chunk_size=300):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    MODEL = "qwen2.5-coder-7b-instruct-mlx"
    updated_lines = []

    for i in range(0, len(lines), chunk_size):
        chunk = "".join(lines[i:i+chunk_size])
        prompt = f"""
Clean trivial TODOs in this Kotlin/Java file.
Follow rules from {rules_path}.
Only modify TODOs, do not change any other code.
Output **only the updated code**, without any explanations, markers, or tokens.
File content:
{chunk}
"""
        try:
            response = requests.post(
                "http://localhost:1234/v1/completions",
                headers={"Authorization": "Bearer lm-studio"},
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "max_tokens": 4096,
                    "temperature": 0.2
                },
                timeout=300
            )
            response.raise_for_status()
        except Exception as e:
            print(f"⚠️ Error calling LM Studio for {file_path} chunk {i}-{i+chunk_size}: {e}")
            updated_lines.extend(lines[i:i+chunk_size])  # zachowaj oryginał
            continue

        data = response.json()
        text = data.get("choices", [{}])[0].get("text", "")

        # -------------------- Clean AI output --------------------
        for token in ["<|im_start|>", "<|im_end|>", "|>"]:
            text = text.replace(token, "")
        text_lines = [line.rstrip() for line in text.splitlines() if line.strip() != ""]

        if text_lines:
            updated_lines.extend(text_lines)
            print(f"✅ Updated chunk {i}-{i+chunk_size} of {file_path}")
        else:
            print(f"⚠️ Empty output for chunk {i}-{i+chunk_size}, keeping original lines")
            updated_lines.extend(lines[i:i+chunk_size])

    # zapis finalnego pliku
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines))
    print(f"🎯 Finished processing {file_path}")

# -------------------- Main --------------------
MAIN_BRANCH = get_main_branch()
DATE_SUFFIX = datetime.datetime.now().strftime("%Y-%m-%d")
BRANCH = f"ai/todo-cleanup/{DATE_SUFFIX}"

print(f"Detected main branch: {MAIN_BRANCH}")
print(f"Creating branch: {BRANCH}")

# Checkout main branch
#sh(f"git fetch origin {MAIN_BRANCH}")
#sh(f"git checkout {MAIN_BRANCH}")
#sh(f"git pull origin {MAIN_BRANCH}")

# Create new branch
sh(f"git checkout -b {BRANCH}")

# Find all TODO files
todo_files = find_todo_files()
if not todo_files:
    print("No TODOs found in app/src. Exiting.")
    sys.exit(0)

# Run AI cleanup on each file
for f in todo_files:
    run_ai_on_file(f)

# Commit changes
sh("git add .")
sh(f"git commit -m 'chore(ai): cleanup TODOs'")

# Push branch (force to avoid non-fast-forward)
sh(f"git push origin {BRANCH} --force")

# Create PR if gh CLI is installed
gh_check = subprocess.run("which gh", shell=True, capture_output=True)
if gh_check.returncode == 0:
    pr_title = "AI: TODO cleanup"
    pr_body = "Safe, minimal automated cleanup"
    sh(f'gh pr create --title "{pr_title}" --body "{pr_body}" --base {MAIN_BRANCH} --head {BRANCH}')
    sh(f"git checkout {MAIN_BRANCH}")
    sh(f"git pull origin {MAIN_BRANCH}")
else:
    print("\nGitHub CLI not found. Open PR manually at:")
    print(f"https://github.com/<YOUR_USER>/<YOUR_REPO>/pull/new/{BRANCH}")
