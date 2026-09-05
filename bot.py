import datetime
import requests

API_KEY = "5e78f9f4bbbc50f46ae1e8bd4b27912d"
TELEGRAM_TOKEN = "8913517520:AAFMJUKyLlzWZna_F9Xemvneejq51jzyeCE"
CHAT_ID = "255781883"

LEAGUES = [
    "soccer_germany_bundesliga",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_epl",
    "soccer_netherlands_eredivisie",
    "soccer_denmark_superliga",
    "soccer_argentina_primera_division",
]


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)


def scan_matches():
    today = datetime.datetime.utcnow().date()
    found_bets = []

    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/"
        params = {
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "h2h,btts",
            "oddsFormat": "decimal",
        }

        res = requests.get(url, params=params)
        if res.status_code != 200:
            continue

        matches = res.json()

        for match in matches:
            commence_time = datetime.datetime.fromisoformat(
                match["commence_time"].replace("Z", "+00:00")
            )
            if commence_time.date() != today:
                continue

            home = match["home_team"]
            away = match["away_team"]
            bookmakers = match.get("bookmakers", [])
            if not bookmakers:
                continue

            markets = bookmakers[0].get("markets", [])

            for market in markets:
                # 1. Filter: Nur Heimsieg (1.50 bis 1.85)
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        if outcome["name"] == home and 1.50 <= outcome["price"] <= 1.85:
                            found_bets.append(
                                f"⚽ *{home} vs. {away}*\n"
                                f"📌 Tipp: Heimsieg ({home})\n"
                                f"📈 Quote: {outcome['price']}\n"
                            )

                # 2. Filter: Beide treffen - JA (1.50 bis 1.85)
                elif market["key"] == "btts":
                    for outcome in market["outcomes"]:
                        if outcome["name"] == "Yes" and 1.50 <= outcome["price"] <= 1.85:
                            found_bets.append(
                                f"⚽ *{home} vs. {away}*\n"
                                f"📌 Tipp: Beide treffen (BTTS: Ja)\n"
                                f"📈 Quote: {outcome['price']}\n"
                            )

    if found_bets:
        header = f"🎯 *Gefilterte Tipps für heute ({today})*:\n\n"
        send_telegram(header + "\n".join(found_bets))
    else:
        send_telegram(f"Heute ({today}) keine Spiele mit Quote 1.50-1.85 gefunden.")


if __name__ == "__main__":
    scan_matches()
