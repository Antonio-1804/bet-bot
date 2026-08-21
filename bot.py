import os
import requests

API_KEY = os.environ.get("ODDS_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SPORTS = [
    "soccer_germany_bundesliga",
    "soccer_germany_bundesliga2",
    "soccer_epl",
    "soccer_efl_champ",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_uefa_champs_league",
    "soccer_france_ligue_one",
    "soccer_netherlands_eredivisie",
    "soccer_denmark_superliga",
    "soccer_norway_eliteserien",
    "soccer_sweden_allsvenskan",
    "soccer_brazil_campeonato",
    "soccer_argentina_primera_division"
]

def get_odds():
    best_bets = []
    
    for sport in SPORTS:
        url = f"https://api.theoddsapi.com/v4/sports/{sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        res = requests.get(url)
        if res.status_code != 200:
            continue
        
        games = res.json()
        
        for game in games:
            home = game.get("home_team")
            away = game.get("away_team")
            bookmakers = game.get("bookmakers", [])
            
            if not bookmakers:
                continue
            
            # Quoten sammeln für Marktdurchschnitt
            odds_pool = {"home": [], "away": [], "draw": []}
            for bm in bookmakers:
                for market in bm.get("markets", []):
                    if market.get("key") == "h2h":
                        for outcome in market.get("outcomes", []):
                            name = outcome.get("name")
                            price = outcome.get("price")
                            if name == home:
                                odds_pool["home"].append(price)
                            elif name == away:
                                odds_pool["away"].append(price)
                            elif name.lower() == "draw":
                                odds_pool["draw"].append(price)
            
            avg = {}
            for key, val in odds_pool.items():
                if len(val) >= 3:
                    avg[key] = sum(val) / len(val)
            
            # Besten Value Bet für DIESES EINE Spiel finden
            game_best_bet = None
            max_value = 0
            
            for bm in bookmakers:
                bm_title = bm.get("title")
                for market in bm.get("markets", []):
                    if market.get("key") == "h2h":
                        for outcome in market.get("outcomes", []):
                            name = outcome.get("name")
                            price = outcome.get("price")
                            
                            target_key = "home" if name == home else ("away" if name == away else "draw")
                            
                            if avg.get(target_key, 0) > 0:
                                val_percent = ((price / avg[target_key]) - 1) * 100
                                
                                # Filter: Mindestens 5% Value, Quote maximal 3.00, nur der stärkste Tipp pro Spiel
                                if val_percent >= 5.0 and 1.20 <= price <= 3.00:
                                    if val_percent > max_value:
                                        max_value = val_percent
                                        game_best_bet = {
                                            "match": f"{home} vs {away}",
                                            "tip": name,
                                            "bookmaker": bm_title,
                                            "price": price,
                                            "avg": avg[target_key],
                                            "value": val_percent
                                        }
            
            if game_best_bet:
                best_bets.append(game_best_bet)
                
    if not best_bets:
        return "Aktuell keine Value Bets (Quote max 3.00) in den Top-Ligen gefunden."
        
    # Sortieren nach höchstem Value
    best_bets = sorted(best_bets, key=lambda x: x["value"], reverse=True)
    
    msg = "🔥 TOP VALUE BETS (Max Quote 3.00):\n\n"
    for b in best_bets[:5]:  # Begrenzt auf die 5 besten Tipps des Tages
        msg += f"⚽ {b['match']}\n"
        msg += f"👉 TIPP: {b['tip']}\n"
        msg += f"🏢 Buchmacher: {b['bookmaker']}\n"
        msg += f"📈 Quote: {b['price']} (Ø: {b['avg']:.2f})\n"
        msg += f"🔥 Value: +{b['value']:.1f}%\n\n"
        
    return msg

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            part = text[i:i+4000]
            requests.post(url, json={"chat_id": CHAT_ID, "text": part})
    else:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})

if __name__ == "__main__":
    message = get_odds()
    send_telegram(message)
    print(message)

