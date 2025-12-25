import requests

file_path = "app/src/main/java/com/example/nieznany_numer/MainActivity.java"

# Wczytaj plik
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Usuń wszystkie dziwne znaczniki przed wysłaniem
for token in ["<|im_start|>", "<|im_end|>", "|>"]:
    content = content.replace(token, "")

# Przygotuj prompt
prompt = f"""
Clean trivial TODOs in this Kotlin/Java file.
Follow rules from ai-agent/rules.md.
Only modify TODOs, do not change other code.
Output only the updated code, without explanations, markers, or tokens.
File content:
{content}
"""

# Wywołanie LM Studio
response = requests.post(
    "http://localhost:1234/v1/completions",
    headers={"Authorization": "Bearer lm-studio"},
    json={
        "model": "qwen2.5-coder-7b-instruct-mlx",
        "prompt": prompt,
        "temperature": 0.2,
        "max_tokens": 4096
    },
    timeout=300
)

data = response.json()
text = data.get("choices", [{}])[0].get("text", "")

print("=== AI OUTPUT START ===")
print(text if text.strip() else "⚠️ EMPTY OUTPUT")
print("=== AI OUTPUT END ===")
