import requests
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

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def fetch_history(coin_id, days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "hourly"}
    data = requests.get(url, params=params).json()
    prices = [p[1] for p in data.get("prices", [])]
    return prices

def support_resistance(prices):
    if not prices or len(prices) < 2:
        return "Нет данных", "Нет данных"
    support = min(prices)
    resistance = max(prices)
    return f"${support:.2f}", f"${resistance:.2f}"

def build_levels_block():
    lines = ["📊 *Ключевые уровни поддержки и сопротивления (7 дней):*"]
    for coin_id, symbol in COINS:
        prices = fetch_history(coin_id, 7)
        support, resistance = support_resistance(prices)
        lines.append(f"{symbol}: Поддержка: {support} | Сопротивление: {resistance}")
    return "\n".join(lines)

def send_levels_block():
    levels_block = build_levels_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": levels_block,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    send_levels_block()
