#!/usr/bin/env python3
import subprocess
from pathlib import Path
from datetime import date
import tempfile
import re

# ---------------- CONFIG ----------------
EXCLUDE_DIRS = {"venv", "ai-agent", ".git", "build", "out", "__pycache__"}
FILE_EXTENSIONS = {".java", ".kt", ".py"}  # rozszerzenia plików, które sprawdzamy
BRANCH_PREFIX = "ai/todo-cleanup"
PROMPT_HEADER = """
You are a senior developer.

TASK:
- Clean ONLY trivial TODOs
- Do NOT change logic or architecture
- Do NOT add new features
- Return the FULL file content
- If TODO cannot be safely resolved, return the file unchanged

FILE:
"""

# ---------------- HELPERS ----------------
def sh(cmd: str):
    """Uruchomienie polecenia w shell z check=True"""
    print(f"> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def find_todo_files(root: Path):
    """Znajdź wszystkie pliki z TODO, ignorując wykluczone foldery"""
    todo_files = []
    for f in root.rglob("*"):
        if f.is_file() and f.suffix in FILE_EXTENSIONS:
            if any(part in EXCLUDE_DIRS for part in f.parts):
                continue
            try:
                if "TODO" in f.read_text(encoding="utf-8"):
                    todo_files.append(f)
            except Exception:
                continue
    return todo_files

def extract_code_from_copilot(text: str) -> str:
    """Wyciąga tylko kod z odpowiedzi Copilot"""
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    if code_blocks:
        return "\n".join(code_blocks)
    return text.strip()  # fallback, jeśli nie ma ``` bloków

# ---------------- MAIN ----------------
if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent.resolve()
    BRANCH = f"{BRANCH_PREFIX}/{date.today().isoformat()}"

    # 1️⃣ Checkout master i aktualizacja
    sh("git fetch origin master")
    sh("git checkout master")
    sh("git pull origin master")

    # 2️⃣ Utworzenie nowego brancha
    sh(f"git checkout -B {BRANCH}")

    # 3️⃣ Znalezienie plików do przetworzenia
    files_to_process = find_todo_files(BASE_DIR)
    if not files_to_process:
        print("Nie znaleziono plików z TODO. Kończę.")
        exit(0)

    # 4️⃣ Przetwarzanie każdego pliku przez Copilot
    for fpath in files_to_process:
        print(f"🧹 Processing {fpath}")
        prompt = PROMPT_HEADER + fpath.read_text(encoding="utf-8")
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as tmp_prompt:
            tmp_prompt.write(prompt)
            tmp_prompt_path = tmp_prompt.name

        tmp_output_path = tmp_prompt_path + "_out.txt"

        # Wywołanie Copilot z -p, obsługa długiego promptu i cudzysłowów
        sh(f'copilot -p @"{tmp_prompt_path}" > "{tmp_output_path}"')

        # Zamiana pliku oryginalnego wygenerowanym przez Copilot
        try:
            raw_output = Path(tmp_output_path).read_text(encoding="utf-8")
            content = extract_code_from_copilot(raw_output)
            fpath.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"Błąd przy zapisie pliku {fpath}: {e}")

    # 5️⃣ Commit i push
    sh("git add .")
    sh('git commit -m "chore(ai): cleanup TODOs"')
    sh(f"git push origin {BRANCH}")

    # 6️⃣ Stworzenie PR na GitHub (gh musi być skonfigurowane)
    sh(f'gh pr create --title "AI: TODO cleanup" --body "Safe, minimal automated cleanup" --base master --head {BRANCH}')

    print("✅ Gotowe!")
