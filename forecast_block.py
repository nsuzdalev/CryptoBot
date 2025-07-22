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
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    data = requests.get(url, params=params).json()
    prices = [p[1] for p in data.get("prices", [])]
    return prices

def simple_forecast(prices):
    if not prices or len(prices) < 3:
        return "Нет данных"
    sma7 = sum(prices) / len(prices)
    sma3 = sum(prices[-3:]) / 3
    if sma3 > sma7 * 1.01:
        return "🟢 Ожидается рост"
    elif sma3 < sma7 * 0.99:
        return "🔻 Ожидается падение"
    else:
        return "⚪ Флэт"

def build_forecast_block():
    lines = ["📈 *Краткосрочный прогноз (7 дней):*"]
    for coin_id, symbol in COINS:
        prices = fetch_history(coin_id, 7)
        forecast = simple_forecast(prices)
        lines.append(f"{symbol}: {forecast}")
    return "\n".join(lines)

def send_forecast_block():
    forecast_block = build_forecast_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": forecast_block,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    send_forecast_block()
