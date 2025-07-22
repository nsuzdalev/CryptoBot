import os
import requests
from datetime import datetime, timedelta
import pytz

# ---- Настройки ----
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
MINSK_TZ = pytz.timezone('Europe/Minsk')

def fetch_market_data():
    ids = ','.join([coin[0] for coin in COINS])
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"}
    return requests.get(url, params=params).json()

def fetch_historical(coin_id, days=7):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "hourly"}
    data = requests.get(url, params=params).json()
    prices = [p[1] for p in data.get("prices",[])]
    timestamps = [p[0] for p in data.get("prices",[])]
    return prices, timestamps

def sma(prices, period=24):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def fetch_btc_dominance():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global")
        return res.json()['data']['market_cap_percentage']['btc']
    except:
        return None

def fetch_news():
    try:
        url = "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=BTC,ETH,ARB,SOL,APT,DOT,W,HFT,LTC,ATOM,ONDO&public=true"
        res = requests.get(url)
        items = res.json().get("results", [])
        news = []
        for item in items:
            if item.get("title") and item.get("domain") not in ["youtube.com"]:
                news.append(f"— {item['title']}")
            if len(news) == 3:
                break
        return news
    except:
        return []

def get_support_resistance(prices):
    if not prices or len(prices) < 2:
        return None, None
    return round(min(prices),2), round(max(prices),2)

def analyze_jumps(prices, hours, threshold):
    if len(prices) < hours + 1:
        return 0
    start = prices[-hours-1]
    end = prices[-1]
    pct = 100 * (end - start) / start if start else 0
    return pct

def build_report():
    now = datetime.now(MINSK_TZ)
    dt = now.strftime('%d.%m.%Y %H:%M')
    market = fetch_market_data()
    dom = fetch_btc_dominance()
    news = fetch_news()
    report = [f"📊 *Криптоотчёт на {dt}* \\(Минск\\)\n"]

    report.append("💰 *Текущие цены и изменение за 24ч*:")
    for coin_id, symbol in COINS:
        price = market.get(coin_id, {}).get("usd", None)
        change = market.get(coin_id, {}).get("usd_24h_change", 0.0)
        # История для прогноза и уровней
        hist, _ = fetch_historical(coin_id, 7)
        # Прогноз (SMA 24ч vs цена)
        forecast = "—"
        if hist and len(hist) >= 48:
            avg = sma(hist, 24)
            direction = "🔺 рост" if hist[-1] > avg else "🔻 падение"
            forecast = f"{direction} (SMA24: ${avg:.2f})"
        # Поддержка/сопротивление за 7 дней
        support, resistance = get_support_resistance(hist[-168:]) if hist else (None, None)
        support_txt = f"Поддержка: ${support}" if support else ""
        resistance_txt = f"Сопротивление: ${resistance}" if resistance else ""
        arrow = "🔺" if change > 0 else "🔻"
        report.append(
            f"{symbol}: ${price:,.2f} ({arrow}{abs(change):.2f}%) | {forecast} | {support_txt} {resistance_txt}"
        )

    # Доминация BTC
    if dom:
        report.append(f"\n📈 *Доминация BTC*: {dom:.2f}%")

    # Блок резких скачков
    jump_lines = []
    for coin_id, symbol in COINS:
        hist, _ = fetch_historical(coin_id, 1)
        pct_1h = analyze_jumps(hist, 1, 10)
        if abs(pct_1h) >= 10:
            jump_lines.append(f"{symbol}: {'🔺' if pct_1h>0 else '🔻'}{pct_1h:.2f}% за 1ч 🚨")
        hist4, _ = fetch_historical(coin_id, 4)
        pct_4h = analyze_jumps(hist4, 4, 5)
        if abs(pct_4h) >= 5:
            jump_lines.append(f"{symbol}: {'🔺' if pct_4h>0 else '🔻'}{pct_4h:.2f}% за 4ч")
    if jump_lines:
        report.append("\n⚡️ *Резкие скачки цен (только если есть)*:")
        report += jump_lines

    # Новости и подтверждения
    if news:
        report.append("\n📰 *Последние новости и сигналы:*")
        report += news

    # Ключевые уровни ликвидаций
    report.append("\n🔑 *Ключевые уровни ликвидаций (волатильность):*")
    for coin_id, symbol in COINS:
        hist, _ = fetch_historical(coin_id, 7)
        if hist and len(hist) > 48:
            week_min = min(hist[-168:])
            week_max = max(hist[-168:])
            day_min = min(hist[-24:])
            day_max = max(hist[-24:])
            report.append(f"{symbol}: день [{day_min:.2f} — {day_max:.2f}], неделя [{week_min:.2f} — {week_max:.2f}]")

    report.append("\n⚠️ *Это не финансовый совет.*")
    return "\n".join(report)

def send_report(text):
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

def main():
    report = build_report()
    send_report(report)

if __name__ == "__main__":
    main()
