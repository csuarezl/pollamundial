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
    "United States": "Estados Unidos", "Bosnia and Herzegovina": "Bosnia", "Bosnia & Herzegovina": "Bosnia",
    "Spain": "España", "Austria": "Austria",
    "Portugal": "Portugal", "Croatia": "Croacia",
    "Switzerland": "Suiza", "Algeria": "Argelia",
    "Australia": "Australia", "Egypt": "Egipto",
    "Argentina": "Argentina", "Cape Verde": "Cabo Verde",
    "Colombia": "Colombia", "Ghana": "Ghana",
}

def translate(name):
    return TEAM_TRANSLATE.get(name, name)

def main():
    req = urllib.request.Request(API_URL, headers={"X-Auth-Token": API_KEY})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    all_matches = data.get("matches", [])
    print(f"Total de partidos recibidos de la API: {len(all_matches)}")

    # Diagnóstico: mostrar las etapas (stage) que existen realmente
    stages_found = sorted(set(m.get("stage", "SIN_STAGE") for m in all_matches))
    print(f"Etapas (stage) encontradas en la API: {stages_found}")

    results = {}
    for match in all_matches:
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
        print(f"Partido finalizado: {key} -> ganador: {winner}")

    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Guardado {len(results)} resultados en total.")

if __name__ == "__main__":
    main()
