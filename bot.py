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

def get_odds():
    all_messages = []
    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
        res = requests.get(url)
        data = res.json()
        
        if isinstance(data, list) and len(data) > 0:
            for match in data:
                home = match.get('home_team')
                away = match.get('away_team')
                all_messages.append(f"⚽ {home} vs {away}")
                
    if not all_messages:
        return "Keine aktuellen Quoten in den Top-Ligen vorhanden."
    
    return "🔥 HEUTIGE QUOTEN:\n\n" + "\n".join(all_messages)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    res = requests.post(url, json=payload)
    print(f"Telegram Status: {res.status_code}")

if __name__ == "__main__":
    msg = get_odds()
    send_telegram(msg)
