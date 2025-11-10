import requests
import json

# === SEU TOKEN DA API ===
FOOTBALL_TOKEN = "41a39808a6454c1abe051e924fc92287"

# === URL da API da tabela do Brasileirão ===
url = "https://api.football-data.org/v4/competitions/BSA/matches"

# === Cabeçalho com o token (obrigatório) ===
headers = {
    "X-Auth-Token": FOOTBALL_TOKEN
}

# === Faz a requisição ===
response = requests.get(url, headers=headers)

# === Verifica se deu certo ===
if response.status_code == 200:
    data = response.json()
    # Mostra o JSON completo formatado (como no navegador)
    print(json.dumps(data, indent=4, ensure_ascii=False))
else:
    print(f"❌ Erro {response.status_code}: {response.text}")
