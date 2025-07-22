import os
import requests
from datetime import datetime, timedelta
import pytz

# --- Настройки монет и названий ---
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

# --- Telegram настройки ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# --- Время для Минска ---
MINSK_TZ = pytz.timezone('Europe/Minsk')
now = datetime.now(MINSK_TZ)

# --- Получение цен, изменений, SMA и истории ---
def fetch_market_data():
    ids = ','.join([coin[0] for coin in COINS])
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    data = requests.get(url, params=params).json()
    return data

def fetch_historical(coin_id, days=7):
    # Получаем цену за последние 7 дней по часам
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

# --- Доминация BTC ---
def fetch_btc_dominance():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global")
        btc_dom = res.json()['data']['market_cap_percentage']['btc']
        return btc_dom
    except:
        return None

# --- Новости и X (Twitter)/CryptoPanic ---
def fetch_news():
    try:
        url = "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=BTC,ETH,ARB,SOL,APT,DOT,W,HFT,LTC,ATOM,ONDO&public=true"
        res = requests.get(url)
        items = res.json().get("results", [])
        news = []
        for item in items[:3]:  # максимум 3 коротких новости
            if item.get("title"):
                news.append(f"— {item['title']}")
        return news
    except:
        return []

# --- Анализ уровней поддержки/сопротивления (простые экстремумы) ---
def get_levels(prices):
    if len(prices) < 2:
        return None, None
    support = min(prices)
    resistance = max(prices)
    return round(support, 2), round(resistance, 2)

# --- Анализ скачков ---
def analyze_jumps(prices, period_hours, threshold):
    if len(prices) < period_hours+1:
        return 0
    start = prices[-period_hours-1]
    end = prices[-1]
    pct = 100 * (end - start) / start if start else 0
    return pct

# --- Главная функция формирования отчёта ---
def build_report():
    dt = now.strftime('%d.%m.%Y %H:%M')
    report = [f"📊 Криптоотчёт на {dt} (время Минск)\n"]

    # Цены, проценты, прогноз, уровни
    market = fetch_market_data()
    report.append("💰 Текущие цены (и изменение за 24ч):")
    for coin_id, symbol in COINS:
        price = market.get(coin_id, {}).get("usd", None)
        change = market.get(coin_id, {}).get("usd_24h_change", 0.0)
        # Исторические цены
        hist, _ = fetch_historical(coin_id, 7)
        # Прогноз (SMA + направление)
        forecast = "—"
        if hist and len(hist) >= 168:  # 7 дней*24ч
            avg = sma(hist, 24)
            direction = "↑" if hist[-1] > avg else "↓"
            forecast = f"{direction} SMA7дн: ${avg:.2f}"
        # Уровни
        support, resistance = get_levels(hist[-168:]) if hist else (None, None)
        arrow = "🔺" if change > 0 else "🔻"
        change_txt = f"{arrow}{abs(change):.2f}%"
        support_txt = f"Поддержка: ${support}" if support else ""
        resistance_txt = f"Сопротивление: ${resistance}" if resistance else ""
        report.append(
            f"{symbol}: ${price:,.2f} ({change_txt}) | {forecast} | {support_txt} {resistance_txt}"
        )

    # Доминация BTC
    dom = fetch_btc_dominance()
    if dom:
        report.append(f"\n📈 Доминация BTC: {dom:.2f}%")

    # Анализ скачков
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
        report.append("\n⚡️ Резкие скачки цен за 1ч и 4ч:")
        report += jump_lines

    # Новости
    news = fetch_news()
    if news:
        report.append("\n📰 Последние надёжные новости и сигналы:")
        report += news

    # Ликвидации (псевдо-уровни)
    report.append("\n🔑 Ключевые уровни ликвидаций (по волатильности):")
    for coin_id, symbol in COINS:
        hist, _ = fetch_historical(coin_id, 7)
        if hist and len(hist) > 48:
            # Примитивная оценка: максимум/минимум дня/недели
            week_min = min(hist[-168:])
            week_max = max(hist[-168:])
            day_min = min(hist[-24:])
            day_max = max(hist[-24:])
            report.append(f"{symbol}: день [{day_min:.2f} — {day_max:.2f}], неделя [{week_min:.2f} — {week_max:.2f}]")

    report.append("\n⚠️ Это не финансовый совет.")
    return "\n".join(report)

# --- Telegram отправка ---
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
