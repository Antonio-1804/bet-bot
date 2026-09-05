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
    now = datetime.datetime.now(datetime.timezone.utc)
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
            time_diff = commence_time - now

            # Spiele der nächsten 36 Stunden erfassen
            if not (
                datetime.timedelta(hours=0)
                <= time_diff
                <= datetime.timedelta(hours=36)
            ):
                continue

            home = match["home_team"]
            away = match["away_team"]
            bookmakers = match.get("bookmakers", [])
            if not bookmakers:
                continue

            # Durchsuche Quoten
            for bm in bookmakers:
                for market in bm.get("markets", []):
                    # 1. Heimsieg (1.45 bis 1.90)
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            if (
                                outcome["name"] == home
                                and 1.45 <= outcome["price"] <= 1.90
                            ):
                                tip = (
                                    f"⚽ *{home} vs. {away}*\n"
                                    f"📌 Tipp: Heimsieg ({home})\n"
                                    f"📈 Quote: {outcome['price']}\n"
                                )
                                if tip not in found_bets:
                                    found_bets.append(tip)

                    # 2. BTTS Ja (1.45 bis 1.90)
                    elif market["key"] == "btts":
                        for outcome in market["outcomes"]:
                            if (
                                outcome["name"] == "Yes"
                                and 1.45 <= outcome["price"] <= 1.90
                            ):
                                tip = (
                                    f"⚽ *{home} vs. {away}*\n"
                                    f"📌 Tipp: Beide treffen (BTTS)\n"
                                    f"📈 Quote: {outcome['price']}\n"
                                )
                                if tip not in found_bets:
                                    found_bets.append(tip)

    if found_bets:
        header = "🎯 *Gefilterte Value-Tipps (nächste 36h)*:\n\n"
        send_telegram(header + "\n".join(found_bets))
    else:
        send_telegram("Keine passenden Quoten (1.45 - 1.90) gefunden.")


if __name__ == "__main__":
    scan_matches()
