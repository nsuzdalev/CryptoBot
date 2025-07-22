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
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
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

def build_forecast_block():
    lines = ["📈 *Краткосрочный прогноз (7 дней):*"]
    for coin_id, symbol in COINS:
        prices = fetch_history_safe(coin_id, 7)
        if prices is None:
            lines.append(f"{symbol}: Данных за неделю нет на CoinGecko")
        elif len(prices) < 3:
            lines.append(f"{symbol}: Недостаточно истории для прогноза")
        else:
            sma7 = sum(prices) / len(prices)
            current = prices[-1]
            min7 = min(prices)
            max7 = max(prices)
            delta_pct = 100 * (current - sma7) / sma7 if sma7 else 0
            if delta_pct > 1:
                direction = "🟢 Ожидается рост"
            elif delta_pct < -1:
                direction = "🔻 Ожидается падение"
            else:
                direction = "⚪ Флэт"
            lines.append(
                f"{symbol}: {direction} ({delta_pct:+.2f}%), диапазон: ${min7:.2f}–${max7:.2f}"
            )
    return "\n".join(lines)

# --- Для отдельного теста, если запускать этот файл напрямую ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

if __name__ == "__main__":
    block = build_forecast_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": block,
        "parse_mode": "Markdown"
    })
