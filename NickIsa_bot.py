import requests
import os
from dotenv import load_dotenv
import time
import random

load_dotenv("token.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FOOTBALL_TOKEN = os.getenv("FOOTBALL_TOKEN")

# ---------------------- Funções Telegram -------------------------

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    """Envia mensagem com parse_mode HTML"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"} #permite que o telegram interprete HTML
    requests.post(url, data=data)

# ---------------------- Funções API Futebol ----------------------
# https://native-stats.org/competition/BSA/
# https://www.football-data.org/documentation/quickstart

def get_tabela():
    url = "https://api.football-data.org/v4/competitions/BSA/standings" #API puxa a atabela de classificação
    headers = {"X-Auth-Token": FOOTBALL_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "Erro ao acessar a API da tabela."

    data = response.json()
    tabela = data.get("standings", [])[0].get("table", [])
    if not tabela:
        return "Não foi possível obter a tabela."

    abreviacoes = {
        "Vasco da Gama": "VAS", "Internacional": "INT", "Corinthians": "COR",
        "Fluminense": "FLU", "Flamengo": "FLA", "São Paulo": "SAO",
        "Botafogo": "BOT", "Palmeiras": "PAL", "Cruzeiro": "CRU",
        "Grêmio": "GRE", "Santos": "SAN", "Bahia": "BAH", "Fortaleza": "FOR",
        "Bragantino": "BRA", "Vitória": "VIT", "Ceará": "CEA",
        "Juventude": "JUV", "Mirassol": "MIR", "Sport Recife": "SPO"
    }

    resposta = "<b>BRASILEIRÃO SÉRIE A</b>\n\n<pre>"
    resposta += f"{'POS':<4}{'TIME':<8}{'PTS':>5}{'PJ':>5}{'VIT':>5}{'E':>5}{'DER':>5}\n"
    resposta += "-" * 38 + "\n"

    for time in tabela:
        pos = time["position"]
        nome_completo = time["team"]["shortName"]
        nome = abreviacoes.get(nome_completo, nome_completo[:3].upper())
        pontos = time["points"]
        jogos = time["playedGames"]
        vitorias = time["won"]
        empates = time["draw"]
        derrotas = time["lost"]

        resposta += f"{pos:<4}{nome:<8}{pontos:>5}{jogos:>5}{vitorias:>5}{empates:>5}{derrotas:>5}\n"

    resposta += "</pre>"
    return resposta

def get_artilheiro():
    import requests

    url = "https://api.football-data.org/v4/competitions/BSA/scorers" 
    headers = {"X-Auth-Token": FOOTBALL_TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Erro ao acessar a API de artilheiros."

    data = response.json()
    artilheiros = data.get("scorers", [])
    if not artilheiros:
        return "Não foi possível obter a lista de artilheiros."

    # Dicionário de abreviações atualizado para bater com nomes da API
    abreviacoes = {
        "Vasco da Gama": "VAS", "Internacional": "INT", "Corinthians": "COR",
        "Fluminense": "FLU", "Flamengo": "FLA", "São Paulo": "SAO",
        "Botafogo": "BOT", "Palmeiras": "PAL", "Cruzeiro": "CRU",
        "Grêmio": "GRE", "Santos": "SAN", "Bahia": "BAH", "Fortaleza": "FOR",
        "Bragantino": "BRA", "Vitória": "VIT", "Ceará": "CEA",
        "Juventude": "JUV", "Mirassol": "MIR", "Sport Recife": "SPO"
    }

    resposta = "<b>ARTILHARIA - BRASILEIRÃO</b>\n\n<pre>"
    resposta += f"{'POS':<4}{'JOGADOR':<20}{'TIME':<8}{'GOLS':>5}\n"
    resposta += "-" * 40 + "\n"

    for i, item in enumerate(artilheiros, start=1):
        jogador = item["player"]["name"][:18]  # limite para não quebrar coluna
        time_nome = item["team"]["shortName"]  # nome completo do time da API
        time_sigla = abreviacoes.get(time_nome, time_nome[:3].upper())
        gols = item["goals"]  # campo correto da API de artilheiros

        # Adiciona cada linha dentro do loop
        resposta += f"{i:<4}{jogador:<20}{time_sigla:<8}{gols:>5}\n"

    resposta += "</pre>"
    return resposta

def get_jogos():
    import requests
    from datetime import datetime, timezone, timedelta
    try:
        from zoneinfo import ZoneInfo  # Python 3.9+
        tz_sp = ZoneInfo("America/Sao_Paulo")
    except Exception:
        tz_sp = timezone(timedelta(hours=-3))  # fallback se não houver zoneinfo

    url = "https://api.football-data.org/v4/competitions/BSA/matches"
    headers = {"X-Auth-Token": FOOTBALL_TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:      
        return "Erro ao acessar a API de jogos."

    data = response.json()
    jogos = data.get("matches", [])
    if not jogos:
        return "Não foi possível obter a lista de jogos."
    
    #pega a hora em UTC  e tranforma no fuso de SP
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc) 
    hoje_sp = now_utc.astimezone(tz_sp).date()

    jogos_por_data = {}

    #vai procurar sem UTC 
    for j in jogos:
        utc_str = j.get("utcDate")
        if not utc_str:
            continue

        # UTC termina com Z, se não estiver vai transformar e se não tiver fuso, ele adicona manualmente 
        try:
            if utc_str.endswith("Z"):
                dt_utc = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            else:
                dt_utc = datetime.fromisoformat(utc_str)
                if dt_utc.tzinfo is None:
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)

        # se o fromato vem diferete, ele corta o ponto e tenta novamente. Se ainda der errro, ele ira pular o jogo 
        except Exception:
            try:
                dt_utc = datetime.strptime(utc_str.split(".")[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            except Exception:
                continue
        
        # conversão para o fuso de SP. Se der erro eel substitui manualmete menos 3 horas 
        try:
            dt_sp = dt_utc.astimezone(tz_sp)
        except Exception:
            dt_sp = (dt_utc + timedelta(hours=-3)).replace(tzinfo=tz_sp)

        # Pega a data local e adiona o j e dt_sp dentro da lista dos jogos daquele dia 
        data_local = dt_sp.date()
        jogos_por_data.setdefault(data_local, []).append((j, dt_sp)) # cria a chave se ela ainda não existir 

    # pega todas  as datas do dionário, ordena e procura a data na qual bate com a ataual 
    datas_ordenadas = sorted(jogos_por_data.keys())
    data_alvo = next((d for d in datas_ordenadas if d >= hoje_sp), None)
    if not data_alvo:
        return "Não há jogos agendados no momento."

    jogos_dia = jogos_por_data[data_alvo]

    resposta = f"<b>JOGOS - {data_alvo.strftime('%d/%m/%Y')}</b>\n\n<pre>"
    resposta += f"{'HORA':<7}{'MANDANTE':>8}{'G':>2} x {'G':<2} {'VISITANTE':<14}\n"
    resposta += "-" * 35 + "\n"

    for item, dt_sp in sorted(jogos_dia, key=lambda x: x[1]):
        hora_jogo = dt_sp.strftime("%H:%M")

        time_casa = item["homeTeam"]["shortName"][:12]
        time_visita = item["awayTeam"]["shortName"][:12]
        placar_casa = item["score"]["fullTime"]["home"]
        placar_visita = item["score"]["fullTime"]["away"]

        resposta += f"{hora_jogo:<7}{time_casa:>8}{(placar_casa or '0'):>2} x {(placar_visita or '0'):<2} {time_visita:<14}\n"

    resposta += "</pre>"
    return resposta

# ---------------------- Loop principal ----------------------------

def main():
    last_update_id = 0

    while True:
        updates = get_updates(last_update_id)
        if "result" in updates and len(updates["result"]) > 0:
            for update in updates["result"]:
                update_id = update["update_id"]
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "").lower()

                print(f"📩 Mensagem recebida: {text} de {chat_id}") 

                # verifica o que foi enviado
                if text == "/tabela":
                    send_message(chat_id, "Buscando classificação do Brasileirão...")
                    send_message(chat_id, get_tabela())
                elif text == "/artilheiro":
                    send_message(chat_id, "Buscando artilheiros do Brasileirão...")
                    send_message(chat_id, get_artilheiro())
                elif text == "/jogos":
                    send_message(chat_id, "Buscando próximos jogos do brasileirão...")
                    send_message(chat_id, get_jogos())
                elif "corinthians" in text or "timão" in text:
                    musicas_corinthians = [
                        (
                            "Salve o Corinthians\n"
                            "O campeão dos campeões\n"
                            "Eternamente dentro dos nossos corações\n\n"
                            "Salve o Corinthians\n"
                            "De tradições e glórias mil\n"
                            "Tu és orgulho dos desportistas do Brasil"
                        ),
                        (
                            "Aqui tem um bando de loucos\n"
                            "Loucos por ti, Corinthians!\n"
                            "Aqueles que acham que é pouco\n"
                            "Eu vivo por ti, Corinthians!"
                        )
                    ]
                    send_message(chat_id, random.choice(musicas_corinthians)) # sorteia uma das músicas 50%/50%
                elif "flamengo" in text or "mengo" in text:
                    send_message(chat_id,
                        "Em dezembro de 81'\n"
                        "Botou os ingleses na roda\n\n"
                        "3 à 0 no Liverpool\n"
                        "Ficou marcado na história\n\n"
                        "E no Rio não tem outro igual\n"
                        "Só Flamengo é campeão mundial\n"
                        "E agora o seu povo\n"
                        "Pede o mundo de novo\n\n"
                        "Dá—lhe, dá—lhe, dá—lhe, Mengo\n"
                        "Pra cima deles, Flamengo")
                elif "botafogo" in text or "fogo" in text:
                    send_message(chat_id,
                        "E ninguém cala'\n"
                        "Esse nosso amor\n"
                        "E é por isso que eu canto assim\n"
                        "É por ti, Fogo\n\n"
                        "Fogo-ô-ô-ô\n"
                        "Fogo-ô-ô-ô")
                else:
                    send_message(chat_id,
                        "<b>Comandos disponíveis:</b>\n"
                        "/tabela – Classificação do Brasileirão \n"
                        "/artilheiro – Artilheiros da competição \n "
                        "/jogos - Veja os próximos jogos")

                last_update_id = update_id + 1

        time.sleep(2)

if __name__ == "__main__":
    main()
