#!/usr/bin/env python3
import subprocess
from pathlib import Path
from datetime import date
import tempfile
import shlex

# ---------- HELPER ----------
def sh(cmd, check=True):
    """Run shell command"""
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=check)

# ---------- CONFIG ----------
# Branch nazwa na podstawie daty
BRANCH = f"ai/todo-cleanup/{date.today().isoformat()}"

# Root repo (aktualny katalog)
ROOT = Path(__file__).parent.parent.resolve()

# ---------- ZBIERANIE PLIKÓW Z TODO ----------
def find_todo_files(root: Path):
    todo_files = []
    for f in root.rglob("*"):
        if f.is_file() and f.suffix in [".java", ".kt", ".py"]:  # dodaj inne rozszerzenia jeśli trzeba
            try:
                if "TODO" in f.read_text(encoding="utf-8"):
                    todo_files.append(f)
            except Exception:
                continue
    return todo_files

FILES = find_todo_files(ROOT)
if not FILES:
    print("Nie znaleziono plików z TODO.")
    exit(0)

print("Znalezione pliki z TODO:")
for f in FILES:
    print(f" - {f.relative_to(ROOT)}")

# ---------- GIT ----------
sh("git fetch origin master")
sh("git checkout master")
sh("git pull origin master")
sh(f"git checkout -B {BRANCH}")

# ---------- GENEROWANIE POPRAWEK PRZEZ COPILOT ----------
for file_path in FILES:
    rel_path = file_path.relative_to(ROOT)
    print(f"🧹 Processing {rel_path}")

    # Przygotowanie promptu
    file_content = file_path.read_text(encoding="utf-8")
    prompt = f"""
You are a senior Android developer.

TASK:
- Clean ONLY trivial TODOs
- Do NOT change logic or architecture
- Do NOT add new features
- Return the FULL file content
- If TODO cannot be safely resolved, return the file unchanged

FILE:
{file_content}
"""
    # Użycie shlex.quote do zabezpieczenia cudzysłowów i spacji
    safe_prompt = shlex.quote(prompt)

    # Plik tymczasowy na wynik
    with tempfile.NamedTemporaryFile("w+", delete=False) as out_file:
        tmp_output = out_file.name

    # Wywołanie Copilot CLI z -p
    sh(f"copilot -p {safe_prompt} > {tmp_output}")

    # Nadpisanie pliku wygenerowanym kodem
    out_text = Path(tmp_output).read_text(encoding="utf-8")
    file_path.write_text(out_text, encoding="utf-8")

# ---------- COMMIT & PUSH ----------
sh("git add .")
sh(f"git commit -m 'chore(ai): cleanup TODOs'")
sh(f"git push origin {BRANCH}")

# ---------- CREATE PR ----------
pr_title = "AI: TODO cleanup"
pr_body = "Safe, minimal automated cleanup"
sh(f'gh pr create --title {shlex.quote(pr_title)} --body {shlex.quote(pr_body)} --base master --head {BRANCH}')

print("✅ Done! PR created.")
