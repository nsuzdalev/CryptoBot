import requests
import time
import os

def fetch_btc_dominance(retries=3):
    url = "https://api.coingecko.com/api/v3/global"
    for _ in range(retries):
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                btc_dom = res.json().get('data', {}).get('market_cap_percentage', {}).get('btc')
                if btc_dom is not None:
                    return btc_dom
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None

def build_btc_dominance_block():
    dom = fetch_btc_dominance()
    if dom is not None:
        return f"🟠 *Доминация Bitcoin (BTC)*: {dom:.2f}%"
    else:
        return "🟠 *Доминация Bitcoin (BTC)*: данные недоступны"

# Отправка блока в Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

if __name__ == "__main__":
    block = build_btc_dominance_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": block,
        "parse_mode": "Markdown"
    })
