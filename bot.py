import datetime
import requests

API_KEY = "5e78f9f4bbbc50f46ae1e8bd4b27912d"
TELEGRAM_TOKEN = "8913517520:AAFMJUKyLlzWZna_F9Xemvneejq51jzyeCE"
CHAT_ID = "255781883"

LEAGUES = [
    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_epl",
    "soccer_netherlands_eredivisie",
    "soccer_denmark_superliga",
    "soccer_uefa_champs_league",
    "soccer_uefa_nations_league"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def scan_matches():
    now = datetime.datetime.now(datetime.timezone.utc)
    found_bets = []

    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/"
        params = {
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "totals,btts",
            "oddsFormat": "decimal"
        }

        res = requests.get(url, params=params)
        if res.status_code != 200:
            continue

        matches = res.json()

        for match in matches:
            commence_time = datetime.datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
            time_diff = commence_time - now

            # Spiele der nächsten 48 Stunden
            if not (datetime.timedelta(hours=0) <= time_diff <= datetime.timedelta(hours=48)):
                continue

            home = match["home_team"]
            away = match["away_team"]
            bookmakers = match.get("bookmakers", [])
            if not bookmakers:
                continue

            for bm in bookmakers:
                for market in bm.get("markets", []):
                    # 1. Über 2.5 Tore (Quote 1.65 bis 1.95)
                    if market["key"] == "totals":
                        for outcome in market.get("outcomes", []):
                            point = outcome.get("point")
                            name = outcome.get("name")
                            price = outcome.get("price", 0)
                            if name == "Over" and point == 2.5 and 1.65 <= price <= 1.95:
                                tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Über 2.5 Tore\n📈 Quote: {price}\n"
                                if tip not in found_bets:
                                    found_bets.append(tip)

                    # 2. Beide Teams treffen (Quote 1.65 bis 1.95)
                    elif market["key"] == "btts":
                        for outcome in market.get("outcomes", []):
                            name = outcome.get("name")
                            price = outcome.get("price", 0)
                            if name == "Yes" and 1.65 <= price <= 1.95:
                                tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Beide treffen: JA (BTTS)\n📈 Quote: {price}\n"
                                if tip not in found_bets:
                                    found_bets.append(tip)

    if found_bets:
        header = "🎯 *Tor-Tipps (Über 2.5 & BTTS | nächste 48h)*:\n\n"
        chunks = [found_bets[i:i + 15] for i in range(0, len(found_bets), 15)]
        for chunk in chunks:
            send_telegram(header + "\n".join(chunk))
            header = ""
    else:
        send_telegram("Aktuell keine passenden Tor-Tipps (Über 2.5 oder BTTS 1.65-1.95) gefunden.")

if __name__ == "__main__":
    scan_matches()
