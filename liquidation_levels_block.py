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

def build_liquidation_levels_block():
    lines = ["🔑 *Ключевые уровни ликвидаций (экстремумы):*"]
    for coin_id, symbol in COINS:
        prices = fetch_history(coin_id, 7)
        if prices and len(prices) >= 24:
            day_prices = prices[-24:]
            week_prices = prices[-168:] if len(prices) >= 168 else prices
            day_min, day_max = min(day_prices), max(day_prices)
            week_min, week_max = min(week_prices), max(week_prices)
            lines.append(
                f"{symbol}: сутки [{day_min:.2f} — {day_max:.2f}], неделя [{week_min:.2f} — {week_max:.2f}]"
            )
        else:
            lines.append(f"{symbol}: нет данных")
    return "\n".join(lines)

def send_liquidation_levels_block():
    levels_block = build_liquidation_levels_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": levels_block,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    send_liquidation_levels_block()
