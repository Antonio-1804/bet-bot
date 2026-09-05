import os
import requests

API_KEY = "5e78f9f4bbbc50f46ae1e8bd4b27912d"
TELEGRAM_TOKEN = "8913517520:AAFMJUKyLlzWZna_F9Xemvneejq51jzyeCE"
CHAT_ID = "255781883"



SPORTS = [
    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_netherlands_eredivisie",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_uefa_champs_league"
]

def send_telegram(text):
    if not text:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": CHAT_ID, "text": text})
    print(f"Telegram Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Telegram Antwort: {res.text}")

def get_top_picks():
    picks = []
    
    for sport in SPORTS:
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds?apiKey={API_KEY}&regions=eu&markets=h2h,totals"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"API Fehler bei {sport}: {res.status_code}")
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
            over_15_odds = []
            over_25_odds = []
            
            for bm in bookmakers:
                for market in bm.get("markets", []):
                    if market.get("key") == "h2h":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == home:
                                home_odds.append(outcome.get("price"))
                            elif outcome.get("name") == away:
                                away_odds.append(outcome.get("price"))
                    elif market.get("key") == "totals":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == "Over":
                                if outcome.get("point") == 1.5:
                                    over_15_odds.append(outcome.get("price"))
                                elif outcome.get("point") == 2.5:
                                    over_25_odds.append(outcome.get("price"))
            
            league_name = sport.replace("soccer_", "").replace("_", " ").upper()

            # 1. Favorit Heimsieg (1.20 - 1.85)
            if home_odds:
                avg_home = sum(home_odds) / len(home_odds)
                if 1.20 <= avg_home <= 1.85:
                    picks.append({
                        "match": f"{home} vs. {away}",
                        "league": league_name,
                        "tipp": f"Sieg 1 ({home})",
                        "quote": round(avg_home, 2),
                        "kategorie": "Favorit Heimsieg"
                    })
            
            # 2. Favorit Auswärtssieg (1.20 - 1.85)
            if away_odds:
                avg_away = sum(away_odds) / len(away_odds)
                if 1.20 <= avg_away <= 1.85:
                    picks.append({
                        "match": f"{home} vs. {away}",
                        "league": league_name,
                        "tipp": f"Sieg 2 ({away})",
                        "quote": round(avg_away, 2),
                        "kategorie": "Favorit Auswärtssieg"
                    })

            # 3. Über 1.5 Tore (1.15 - 1.50)
            if over_15_odds:
                avg_o15 = sum(over_15_odds) / len(over_15_odds)
                if 1.15 <= avg_o15 <= 1.50:
                    picks.append({
                        "match": f"{home} vs. {away}",
                        "league": league_name,
                        "tipp": "Über 1.5 Tore",
                        "quote": round(avg_o15, 2),
                        "kategorie": "Tor-Tipp (<1.5)"
                    })

            # 4. Über 2.5 Tore (1.40 - 1.85)
            if over_25_odds:
                avg_o25 = sum(over_25_odds) / len(over_25_odds)
                if 1.40 <= avg_o25 <= 1.85:
                    picks.append({
                        "match": f"{home} vs. {away}",
                        "league": league_name,
                        "tipp": "Über 2.5 Tore",
                        "quote": round(avg_o25, 2),
                        "kategorie": "Tor-Tipp (<2.5)"
                    })

    if not picks:
        return "🤖 Bot-Status: Bot läuft fehlerfrei! Für heute wurden keine passenden Quoten gefunden."

    picks = sorted(picks, key=lambda x: x["quote"])
    top_picks = picks[:10]
    
    msg = "📊 TOP-TIPPS & ANALYSEN DES TAGES:\n\n"
    for p in top_picks:
        msg += f"⚽ {p['match']}\n"
        msg += f"🏆 Liga: {p['league']}\n"
        msg += f"👉 TIPP: {p['tipp']}\n"
        msg += f"📈 Ø-Quote: {p['quote']}\n"
        msg += f"📌 Typ: {p['kategorie']}\n\n"
        
    return msg

if __name__ == "__main__":
    message = get_top_picks()
    send_telegram(message)
    print(message)
