import subprocess
import datetime

TASK = "todo-cleanup"
BRANCH = f"ai/{TASK}/{datetime.date.today()}"

def sh(cmd):
    print(">", cmd)
    subprocess.run(cmd, shell=True, check=True)

# 1. aktualny main
sh("git checkout master")
sh("git pull origin master")

# 2. branch
sh(f"git checkout -b {BRANCH}")

# 3. 🔴 TU NA RAZIE RĘCZNIE
print("""
=== AGENT PAUSE ===
👉 Teraz:
- użyj Continue / LM Studio
- wykonaj zadanie: TODO cleanup
- zapisz pliki
===================
""")
input("Press ENTER when ready...")

# 4. sprawdź czy coś się zmieniło
status = subprocess.check_output("git status --porcelain", shell=True).decode()
if not status.strip():
    print("No changes detected. Aborting.")
    sh("git checkout master")
    sh(f"git branch -D {BRANCH}")
    exit(0)

# 5. commit
sh("git add .")
sh("git commit -m 'chore(ai): cleanup TODOs'")
sh(f"git push origin {BRANCH}")

# 6. PR (bez merge!)
sh(f"""
gh pr create \
  --title "AI: TODO cleanup" \
  --body "Safe, minimal automated cleanup" \
  --base master \
  --head {BRANCH}
""")

print("✅ PR created. Review it manually.")
