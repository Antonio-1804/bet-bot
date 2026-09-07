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
            "markets": "h2h,totals,btts",
            "oddsFormat": "decimal"
        }

        res = requests.get(url, params=params)
        if res.status_code != 200:
            continue

        matches = res.json()

        for match in matches:
            commence_time = datetime.datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
            time_diff = commence_time - now

            # Nächste 7 Tage
            if not (datetime.timedelta(hours=0) <= time_diff <= datetime.timedelta(days=7)):
                continue

            home = match["home_team"]
            away = match["away_team"]
            bookmakers = match.get("bookmakers", [])
            if not bookmakers:
                continue

            match_done = False
            for bm in bookmakers:
                if match_done:
                    break
                for market in bm.get("markets", []):
                    # 1. Über 2.5 Tore (1.65 - 1.95)
                    if market["key"] == "totals":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == "Over" and outcome.get("point") == 2.5:
                                p = outcome.get("price", 0)
                                if 1.65 <= p <= 1.95:
                                    tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Über 2.5 Tore\n📈 Quote: {p}\n"
                                    if tip not in found_bets:
                                        found_bets.append(tip)
                                        match_done = True
                                        break

                    # 2. Beide treffen: JA (1.65 - 1.95)
                    elif market["key"] == "btts":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == "Yes":
                                p = outcome.get("price", 0)
                                if 1.65 <= p <= 1.95:
                                    tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Beide treffen: JA\n📈 Quote: {p}\n"
                                    if tip not in found_bets:
                                        found_bets.append(tip)
                                        match_done = True
                                        break

                    # 3. Solider Favoritensieg (1.55 - 2.15)
                    elif market["key"] == "h2h":
                        for outcome in market.get("outcomes", []):
                            p = outcome.get("price", 0)
                            name = outcome.get("name")
                            if 1.55 <= p <= 2.15 and name in [home, away]:
                                tip = f"⚽ *{home} vs. {away}*\n📌 Tipp: Sieg {name}\n📈 Quote: {p}\n"
                                if tip not in found_bets:
                                    found_bets.append(tip)
                                    match_done = True
                                    break

    if found_bets:
        header = "🎯 *Top-Tipps (nächste 7 Tage)*:\n\n"
        chunks = [found_bets[i:i + 15] for i in range(0, len(found_bets), 15)]
        for chunk in chunks:
            send_telegram(header + "\n".join(chunk))
            header = ""
    else:
        send_telegram("Aktuell keine passenden Quoten für die nächsten 7 Tage gefunden.")

if __name__ == "__main__":
    scan_matches()
