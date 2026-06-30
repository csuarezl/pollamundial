"""
Consulta football-data.org por los resultados del Mundial 2026 (16avos de final)
y genera resultados.json con el ganador de cada partido ya jugado.
Se ejecuta automáticamente vía GitHub Actions.
"""
import json
import os
import urllib.request

API_KEY = os.environ["FOOTBALL_API_KEY"]
API_URL = "https://api.football-data.org/v4/competitions/WC/matches"

# Mapeo de nuestros 16 partidos a los equipos (en inglés, como los devuelve la API)
TEAM_TRANSLATE = {
    "South Africa": "Sudáfrica", "Canada": "Canadá",
    "Brazil": "Brasil", "Japan": "Japón",
    "Germany": "Alemania", "Paraguay": "Paraguay",
    "Netherlands": "Países Bajos", "Morocco": "Marruecos",
    "Ivory Coast": "Costa de Marfil", "Côte d'Ivoire": "Costa de Marfil", "Norway": "Noruega",
    "France": "Francia", "Sweden": "Suecia",
    "Mexico": "México", "Ecuador": "Ecuador",
    "England": "Inglaterra", "DR Congo": "RD del Congo", "Congo DR": "RD del Congo",
    "Belgium": "Bélgica", "Senegal": "Senegal",
    "United States": "Estados Unidos", "Bosnia and Herzegovina": "Bosnia", "Bosnia & Herzegovina": "Bosnia", "Bosnia-Herzegovina": "Bosnia",
    "Spain": "España", "Austria": "Austria",
    "Portugal": "Portugal", "Croatia": "Croacia",
    "Switzerland": "Suiza", "Algeria": "Argelia",
    "Australia": "Australia", "Egypt": "Egipto",
    "Argentina": "Argentina", "Cape Verde": "Cabo Verde",
    "Colombia": "Colombia", "Ghana": "Ghana",
    # Equipos adicionales que aparecen en la fase de grupos (no en 16avos, pero por si acaso)
    "South Korea": "Corea del Sur", "Czechia": "Chequia", "Turkey": "Turquía",
    "Curaçao": "Curazao", "Haiti": "Haití", "Scotland": "Escocia",
    "Iraq": "Irak", "Jordan": "Jordania", "Panama": "Panamá",
    "Uzbekistan": "Uzbekistán", "Tunisia": "Túnez", "Qatar": "Catar",
    "Saudi Arabia": "Arabia Saudita", "New Zealand": "Nueva Zelanda",
    "Uruguay": "Uruguay",
}

def translate(name):
    return TEAM_TRANSLATE.get(name, name)

def main():
    req = urllib.request.Request(API_URL, headers={"X-Auth-Token": API_KEY})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    all_matches = data.get("matches", [])
    print(f"Total de partidos recibidos de la API: {len(all_matches)}")

    last16_matches = [m for m in all_matches if m.get("stage") == "LAST_16"]
    print(f"Partidos en LAST_16: {len(last16_matches)}")
    for m in last16_matches:
        home = translate(m["homeTeam"]["name"])
        away = translate(m["awayTeam"]["name"])
        print(f"  - {home} vs {away} | status: {m.get('status')} | winner: {m.get('score',{}).get('winner')}")

    results = {}
    for match in all_matches:
        if match.get("stage") != "LAST_16":
            continue
        status = match.get("status")
        if status != "FINISHED":
            continue
        home = translate(match["homeTeam"]["name"])
        away = translate(match["awayTeam"]["name"])
        score = match.get("score", {})
        winner_code = score.get("winner")  # HOME_TEAM, AWAY_TEAM, DRAW
        if winner_code == "HOME_TEAM":
            winner = home
        elif winner_code == "AWAY_TEAM":
            winner = away
        else:
            # Empate -> revisar penales
            pen = score.get("penalties", {})
            if pen.get("home") is not None and pen.get("away") is not None:
                winner = home if pen["home"] > pen["away"] else away
            else:
                continue  # sin definir aún
        key = f"{home}|{away}"
        results[key] = winner
        print(f"16avo finalizado: {key} -> ganador: {winner}")

    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Guardado {len(results)} resultados de 16avos.")

if __name__ == "__main__":
    main()
