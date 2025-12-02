#Código de teste
import requests
import json

FOOTBALL_TOKEN = ""

url = "https://api.football-data.org/v4/competitions/BSA/matches"

headers = {
    "X-Auth-Token": FOOTBALL_TOKEN
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()

    print(json.dumps(data, indent=4, ensure_ascii=False))
else:
    print(f"❌ Erro {response.status_code}: {response.text}")
