import os
import datetime
import requests

# Liest Werte aus GitHub Secrets oder nutzt die Fallbacks
API_KEY = os.getenv("ODDS_API_KEY", "5e78f9f4bbbc50f46ae1e8bd4b27912d")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8913517520:AAFMOUkyl1zkMZna_F9Xemvneejq51jzyeCE")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "255781883")

LEAGUES = [
    # Deutschland
    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",
    # Niederlande
    "soccer_netherlands_eredivisie",
    # Schweiz
    "soccer_switzerland_superleague",
]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, json=payload)
    print(f"Telegram-Status: {res.status_code}, Antwort: {res.text}")

def scan_matches():
    now = datetime.datetime.now(datetime.timezone.utc)
    found_bets = []

    print("Starte Liga-Scan...")
    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/"
        params = {
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "totals",
            "oddsFormat": "decimal"
        }

        res = requests.get(url, params=params)
        print(f"Liga: {league} | HTTP-Status: {res.status_code}")

        if res.status_code != 200:
            print(f"Fehler bei Liga {league}: {res.text}")
            continue

        matches = res.json()
        print(f"-> {len(matches)} Spiele in {league} gefunden.")

        for match in matches:
            commence_time = datetime.datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
            time_diff = commence_time - now

            # Spiele der nächsten 7 Tage prüfen
            if not (datetime.timedelta(hours=0) <= time_diff <= datetime.timedelta(days=7)):
                continue

            home = match.get("home_team")
            away = match.get("away_team")
            bookmakers = match.get("bookmakers", [])
            if not bookmakers:
                continue

            match_done = False
            for bm in bookmakers:
                for market in bm.get("markets", []):
                    if market.get("key") == "totals":
                        for outcome in market.get("outcomes", []):
                            # Filter für Über 2.5 Tore und Quote zwischen 1.40 und 1.55
                            if outcome.get("name") == "Over" and outcome.get("point") == 2.5:
                                p = outcome.get("price", 0)
                                if 1.40 <= p <= 1.55:
                                    tip = f"⚽ *{home}* vs. *{away}*\n🎯 Tipp: Über 2.5 Tore\n📊 Quote: {p}\n"
                                    if tip not in found_bets:
                                        found_bets.append(tip)
                                        match_done = True
                                        break
                        if match_done:
                            break
                if match_done:
                    break

    print(f"Gesamtanzahl gefundener Tipps: {len(found_bets)}")

    # Maximal 5 Spiele versenden
    if found_bets:
        top_5 = found_bets[:5]
        header = "🔥 *Top 5 Über 2.5 Tipps (nächste 7 Tage):*\n\n"
        message = header + "\n".join(top_5)
        send_telegram(message)
    else:
        send_telegram("Aktuell keine passenden Quoten (1.40 - 1.55) für Über 2.5 in DE/NL/CH gefunden.")

if __name__ == "__main__":
    scan_matches()
