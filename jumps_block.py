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

def fetch_history(coin_id, hours):
    import time
    now = int(time.time())
    past = now - hours * 3600
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {"vs_currency": "usd", "from": past, "to": now}
    data = requests.get(url, params=params).json()
    prices = [p[1] for p in data.get("prices", [])]
    return prices

def analyze_jumps(prices, period):
    if not prices or len(prices) < 2:
        return 0
    start, end = prices[0], prices[-1]
    if start == 0: return 0
    pct = 100 * (end - start) / start
    return pct

def build_jumps_block():
    lines = []
    for coin_id, symbol in COINS:
        # 4 часа
        prices_4h = fetch_history(coin_id, 4)
        jump_4h = analyze_jumps(prices_4h, 4)
        if abs(jump_4h) >= 5:
            direction = "🟢" if jump_4h > 0 else "🔻"
            lines.append(f"{symbol}: {direction}{abs(jump_4h):.2f}% за 4ч")
        # 1 час (алерт)
        prices_1h = fetch_history(coin_id, 1)
        jump_1h = analyze_jumps(prices_1h, 1)
        if abs(jump_1h) >= 10:
            direction = "🟢" if jump_1h > 0 else "🔻"
            lines.append(f"{symbol}: {direction}{abs(jump_1h):.2f}% за 1ч 🚨")
    if lines:
        header = "⚡️ *Резкие скачки цен за 4ч/1ч (только если есть):*"
        return "\n".join([header] + lines)
    else:
        return "⚡️ Резких скачков цен не обнаружено."

def send_jumps_block():
    jumps_block = build_jumps_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": jumps_block,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    send_jumps_block()
