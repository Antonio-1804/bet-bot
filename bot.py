import requests

TELEGRAM_TOKEN = "DEIN_TELEGRAM_TOKEN"  # Trage hier deinen Bot-Token ein
CHAT_ID = "255781883"
ODDS_API_KEY = "DEIN_ODDS_API_KEY"      # Trage hier deinen Odds-API-Key ein

# Alle gewünschten Ligen:
LEAGUES = [
    "soccer_germany_bundesliga",       # Deutschland
    "soccer_epl",                      # England
    "soccer_spain_la_liga",            # Spanien
    "soccer_italy_serie_a",            # Italien
    "soccer_france_ligue_one",         # Frankreich
    "soccer_netherlands_eredivisie"    # Niederlande
]

def get_odds():
    all_msg = "🔥 VALUE BET EMPFEHLUNGEN:\n\n"
    value_found = False

    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
        try:
            res = requests.get(url)
            data = res.json()
        except Exception:
            continue

        if not isinstance(data, list):
            continue

        for match in data:
            home = match.get('home_team')
            away = match.get('away_team')
            bookmakers = match.get('bookmakers', [])
            
            if not bookmakers:
                continue

            odds_sum = {'home': 0, 'draw': 0, 'away': 0}
            counts = {'home': 0, 'draw': 0, 'away': 0}

            for bm in bookmakers:
                for market in bm.get('markets', []):
                    for outcome in market.get('outcomes', []):
                        name = outcome.get('name')
                        price = outcome.get('price')
                        if name == home:
                            odds_sum['home'] += price
                            counts['home'] += 1
                        elif name == away:
                            odds_sum['away'] += price
                            counts['away'] += 1
                        elif name == 'Draw':
                            odds_sum['draw'] += price
                            counts['draw'] += 1

            avg = {k: (odds_sum[k] / counts[k]) if counts[k] > 0 else 0 for k in odds_sum}

            for bm in bookmakers:
                bm_title = bm.get('title')
                for market in bm.get('markets', []):
                    for outcome in market.get('outcomes', []):
                        name = outcome.get('name')
                        price = outcome.get('price')
                        
                        target_key = 'home' if name == home else ('away' if name == away else 'draw')
                        if avg.get(target_key, 0) > 0:
                            value = ((price / avg[target_key]) - 1) * 100
                            if value >= 5.0:
                                value_found = True
                                all_msg += f"⚽ {home} vs {away}\n"
                                all_msg += f"👉 TIPP: {name}\n"
                                all_msg += f"🏢 Buchmacher: {bm_title}\n"
                                all_msg += f"📈 Quote: {price} (Ø: {avg[target_key]:.2f})\n"
                                all_msg += f"🔥 Value: +{value:.1f}%\n\n"

    if not value_found:
        return "Aktuell keine Value Bets (>5% Abweichung) in den Ligen gefunden."

    return all_msg

def send_telegram(text):
    # Telegram teilt lange Nachrichten bei Bedarf
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    msg = get_odds()
    send_telegram(msg)
    print(msg)
