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

def fetch_market_data():
    ids = ','.join([coin[0] for coin in COINS])
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"}
    return requests.get(url, params=params).json()

def build_prices_block():
    market = fetch_market_data()
    lines = ["💰 *Текущие цены и изменение за 24ч:*"]
    for coin_id, symbol in COINS:
        price = market.get(coin_id, {}).get("usd", None)
        change = market.get(coin_id, {}).get("usd_24h_change", 0.0)
        arrow = "🟢" if change > 0 else "🔻"
        lines.append(f"{symbol}: ${price:,.2f} ({arrow}{abs(change):.2f}%)")
    return "\n".join(lines)

def send_prices_block():
    prices_block = build_prices_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": prices_block,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    send_prices_block()
