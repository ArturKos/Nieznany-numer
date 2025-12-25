#!/usr/bin/env python3
import subprocess
import tempfile
from pathlib import Path
from datetime import date

# --- pomocnicze funkcje ---
def sh(cmd, **kwargs):
    """Uruchamia polecenie w shellu i wyrzuca wyjątek przy błędzie."""
    subprocess.run(cmd, shell=True, check=True, **kwargs)

def git_current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

def get_todo_files():
    """Zwraca listę plików, które zawierają TODO."""
    result = subprocess.run(
        ["git", "grep", "-l", "TODO"],
        capture_output=True, text=True
    )
    files = result.stdout.strip().splitlines()
    return [f for f in files if Path(f).is_file()]

# --- główna logika ---
BRANCH = f"ai/todo-cleanup/{date.today().isoformat()}"
FILES = get_todo_files()

if not FILES:
    print("Brak plików z TODO. Nic do zrobienia.")
    exit(0)

print("Detected main branch:", git_current_branch())
print("Creating branch:", BRANCH)

# przełącz się na master i pull
sh("git fetch origin master")
sh("git checkout master")
sh("git pull origin master")
sh(f"git checkout -B {BRANCH}")

for file_path in FILES:
    print(f"🧹 Processing {file_path}")

    # Tworzymy tymczasowy plik z promptem dla Copilot
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_prompt_file:
        tmp_prompt_file.write(
            f"""
You are a senior Android developer.

TASK:
- Clean ONLY trivial TODOs
- Do NOT change logic or architecture
- Do NOT add new features
- Return the FULL file content
- If TODO cannot be safely resolved, return the file unchanged

FILE:
{Path(file_path).read_text()}
"""
        )
        tmp_prompt_path = tmp_prompt_file.name

    # Tymczasowy plik na wyjście Copilot
    tmp_output = tempfile.NamedTemporaryFile(delete=False).name

    # Wywołanie Copilot w trybie interaktywnym, zapis do pliku
    with open(tmp_output, "w") as out_file:
        subprocess.run(
            ["copilot", "-i", tmp_prompt_path, "--non-interactive"],
            stdout=out_file,
            check=True
        )

    # Nadpisanie pliku wynikiem
    new_content = Path(tmp_output).read_text()
    Path(file_path).write_text(new_content)
    print(f"✅ Updated {file_path}")

# commit + push
sh("git add " + " ".join(FILES))
sh(f"git commit -m 'chore(ai): cleanup TODOs'")
sh(f"git push origin {BRANCH}")

# utworzenie PR
sh(f"""
gh pr create \
--title "AI: TODO cleanup" \
--body "Safe, minimal automated cleanup" \
--base master \
--head {BRANCH}
""")

print("🎉 Done. PR created.")
