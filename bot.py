import os
import requests

API_KEY = os.environ.get("ODDS_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Deine Wunsch-Ligen
SPORTS = [
    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_netherlands_eredivisie",
    "soccer_denmark_superliga",
    "soccer_norway_eliteserien",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_uefa_champs_league"
]

def get_top_picks():
    picks = []
    
    for sport in SPORTS:
        url = f"https://api.theoddsapi.com/v4/sports/{sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,totals"
        res = requests.get(url)
        if res.status_code != 200:
            continue
            
        games = res.json()
        
        for game in games:
            home = game.get("home_team")
            away = game.get("away_team")
            bookmakers = game.get("bookmakers", [])
            
            if not bookmakers:
                continue
                
            home_odds = []
            away_odds = []
            
            for bm in bookmakers:
                for market in bm.get("markets", []):
                    if market.get("key") == "h2h":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == home:
                                home_odds.append(outcome.get("price"))
                            elif outcome.get("name") == away:
                                away_odds.append(outcome.get("price"))
            
            # Favorit Heimsieg (Quote zwischen 1.25 und 1.80)
            if home_odds:
                avg_home = sum(home_odds) / len(home_odds)
                if 1.25 <= avg_home <= 1.80:
                    picks.append({
                        "match": f"{home} vs. {away}",
                        "league": sport.replace("soccer_", "").replace("_", " ").upper(),
                        "tipp": f"Sieg {home}",
                        "quote": round(avg_home, 2),
                        "kategorie": "Klarer Favorit"
                    })
            
            # Favorit Auswärtssieg (Quote zwischen 1.25 und 1.80)
            if away_odds:
                avg_away = sum(away_odds) / len(away_odds)
                if 1.25 <= avg_away <= 1.80:
                    picks.append({
                        "match": f"{home} vs. {away}",
                        "league": sport.replace("soccer_", "").replace("_", " ").upper(),
                        "tipp": f"Sieg {away}",
                        "quote": round(avg_away, 2),
                        "kategorie": "Klarer Favorit"
                    })

    if not picks:
        return "Aktuell keine passenden Favoriten-Spiele in den ausgewählten Ligen gefunden."

    # Sortieren nach den sichersten Quoten (niedrigste zuerst)
    picks = sorted(picks, key=lambda x: x["quote"])
    
    # Auf die besten 8 Spiele begrenzen
    top_picks = picks[:8]
    
    msg = "📊 TOP-FAVORITEN & ANALYSEN DES TAGES:\n\n"
    for p in top_picks:
        msg += f"⚽ {p['match']}\n"
        msg += f"🏆 Liga: {p['league']}\n"
        msg += f"👉 TIPP: {p['tipp']}\n"
        msg += f"📈 Ø-Quote: {p['quote']}\n"
        msg += f"📌 Typ: {p['kategorie']}\n\n"
        
    return msg

def send_telegram(text):
    if not text or "Aktuell keine" in text:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    message = get_top_picks()
    send_telegram(message)
    print(message)
