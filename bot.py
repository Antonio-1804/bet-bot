import requests

TELEGRAM_TOKEN = "8913517520:AAFMJUKyLlzWZna_F9Xemvneejq51jzyeCE"
CHAT_ID = "255781883"
ODDS_API_KEY = "fceda6486f352916f95f8fc82100c"

LEAGUES = [
    "soccer_germany_bundesliga",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a"
]

def get_odds_and_predictions():
    messages = []
    
    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
        res = requests.get(url)
        data = res.json()
        
        if isinstance(data, list) and len(data) > 0:
            for match in data[:3]:  # Top 3 Spiele pro Liga
                home = match.get('home_team')
                away = match.get('away_team')
                
                # Quoten auslesen
                bookmakers = match.get('bookmakers', [])
                if bookmakers:
                    outcomes = bookmakers[0]['markets'][0]['outcomes']
                    home_odds = next((o['price'] for o in outcomes if o['name'] == home), None)
                    away_odds = next((o['price'] for o in outcomes if o['name'] == away), None)
                    draw_odds = next((o['price'] for o in outcomes if o['name'] == 'Draw'), None)
                    
                    # Prognose basierend auf den Quoten berechnen
                    if home_odds and away_odds:
                        if home_odds < away_odds:
                            prog = f"💡 Prognose: Tendenz {home} (Favorit)"
                        else:
                            prog = f"💡 Prognose: Tendenz {away} (Favorit)"
                    else:
                        prog = "💡 Prognose: Ausgeglichen"

                    text = (
                        f"⚽ **{home} vs {away}**\n"
                        f"📊 Quoten: 1: {home_odds} | X: {draw_odds} | 2: {away_odds}\n"
                        f"{prog}\n"
                        f"----------------------------"
                    )
                    messages.append(text)
                
    if not messages:
        return "Keine aktuellen Quoten oder Spiele gefunden."
    
    return "🔥 **QUOTEN & PROGNOSEN HEUTE** 🔥\n\n" + "\n\n".join(messages)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    msg = get_odds_and_predictions()
    send_telegram(msg)
