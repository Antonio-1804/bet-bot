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
    "soccer_uefa_nations_league",
    "soccer_argentina_primera_division",
    "soccer_brazil_campeonato"
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
            "markets": "h2h,btts",
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
                    # 1. Sieg-Wetten (Heim oder Auswärts, 1.30 bis 2.15)
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            price = outcome["price"]
                            if 1.30 <= price <= 2.15:
                                if outcome["name"] == home:
                                    tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Heimsieg ({home})\n📈 Quote: {price}\n"
                                    if tip not in found_bets:
                                        found_bets.append(tip)
                                elif outcome["name"] == away:
                                    tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Auswärtssieg ({away})\n📈 Quote: {price}\n"
                                    if tip not in found_bets:
                                        found_bets.append(tip)

                    # 2. Beide treffen (BTTS: Ja, 1.40 bis 2.10)
                    elif market["key"] == "btts":
                        for outcome in market["outcomes"]:
                            price = outcome["price"]
                            if outcome["name"] == "Yes" and 1.40 <= price <= 2.10:
                                tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Beide treffen (BTTS)\n📈 Quote: {price}\n"
                                if tip not in found_bets:
                                    found_bets.append(tip)

    if found_bets:
        # Nachricht splitten, falls mehr als 15 Spiele gefunden werden
        header = "🎯 *Gefilterte Wett-Tipps (nächste 48h)*:\n\n"
        chunks = [found_bets[i:i + 15] for i in range(0, len(found_bets), 15)]
        for chunk in chunks:
            send_telegram(header + "\n".join(chunk))
            header = ""
    else:
        send_telegram("Aktuell keine anstehenden Spiele im Quotenbereich 1.30-2.15 gefunden.")

if __name__ == "__main__":
    scan_matches()
