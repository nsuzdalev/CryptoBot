import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def fetch_btc_dominance():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global")
        btc_dom = res.json()['data']['market_cap_percentage']['btc']
        return btc_dom
    except Exception:
        return None

def build_btc_dominance_block():
    dom = fetch_btc_dominance()
    if dom is not None:
        return f"🟠 *Доминация Bitcoin (BTC)*: {dom:.2f}%"
    else:
        return "🟠 *Доминация Bitcoin (BTC)*: данные недоступны"

def send_btc_dominance_block():
    dom_block = build_btc_dominance_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": dom_block,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    send_btc_dominance_block()
