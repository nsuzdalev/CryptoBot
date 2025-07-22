import requests
import time
import os

COINS = [
    ('bitcoin', 'BTC'),
    ('ethereum', 'ETH'),
    ('arbitrum', 'ARB'),
    ('solana', 'SOL'),
    ('aptos', 'APT'),
    ('polkadot', 'DOT'),
    ('wormhole', 'W'),
    ('hashflow', 'HFT'),
    ('litecoin', 'LTC'),
    ('cosmos', 'ATOM'),
    ('ondo-finance', 'ONDO')
]

def fetch_history_safe(coin_id, days=7, retries=3):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "hourly"}
    for _ in range(retries):
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                prices = [p[1] for p in data.get("prices", [])]
                if prices:
                    return prices
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None

def build_levels_block():
    lines = ["📊 *Ключевые уровни поддержки и сопротивления (7 дней):*"]
    for coin_id, symbol in COINS:
        prices = fetch_history_safe(coin_id, 7)
        if prices is None:
            support = resistance = "Данных нет на CoinGecko"
        elif len(prices) < 10:
            support = resistance = "Недостаточно данных для расчёта"
        else:
            support = f"${min(prices):.2f}"
            resistance = f"${max(prices):.2f}"
        lines.append(f"{symbol}: Поддержка: {support} | Сопротивление: {resistance}")
    return "\n".join(lines)

# Отправка блока в Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

if __name__ == "__main__":
    block = build_levels_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": block,
        "parse_mode": "Markdown"
    })
