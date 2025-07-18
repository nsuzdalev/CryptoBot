import os
import requests
from datetime import datetime
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_report():
    today = datetime.now().strftime("%d.%m.%Y %H:%M")
    return f"""🗓 Криптоотчёт на {today}

📉 BTC: $119,000
📈 ETH: $3,613
📊 ARB: $0.467
🔥 SOL: $179.5
📌 APT, DOT: +3–7%
🧪 W, HFT: в диапазоне
🟣 LTC, ATOM, ONDO: стабильны

⚠️ Это не финсовет.
"""


def send_report():
    message = get_report()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    send_report()
