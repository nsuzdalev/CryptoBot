import os
import requests
import time
from datetime import datetime, timedelta
import pytz

TOKENS = ['BTC', 'ETH', 'ARB', 'SOL', 'APT', 'DOT', 'W', 'HFT', 'LTC', 'ATOM', 'ONDO']
COINGECKO_IDS = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'ARB': 'arbitrum', 'SOL': 'solana',
    'APT': 'aptos', 'DOT': 'polkadot', 'W': 'wormhole', 'HFT': 'hashflow',
    'LTC': 'litecoin', 'ATOM': 'cosmos', 'ONDO': 'ondo-finance'
}

CHAT_ID = os.getenv("CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Получение текущих цен
def fetch_current_prices():
    ids = ','.join(COINGECKO_IDS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    res = requests.get(url)
    data = res.json()
    return {symbol: data[COINGECKO_IDS[symbol]]['usd'] for symbol in TOKENS}

# Получение исторических данных для анализа скачков
def fetch_historical(symbol_id, hours_ago):
    now = int(time.time())
    past = now - hours_ago * 3600
    url = f"https://api.coingecko.com/api/v3/coins/{symbol_id}/market_chart/range?vs_currency=usd&from={past}&to={now}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    prices = res.json().get('prices', [])
    return prices

# Расчёт % изменения цены
def calculate_price_change(prices):
    if not prices or len(prices) < 2:
        return 0
    start_price = prices[0][1]
    end_price = prices[-1][1]
    if start_price == 0:
        return 0
    return ((end_price - start_price) / start_price) * 100

# Получение доминации BTC
def fetch_btc_dominance():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global")
        btc_dominance = res.json()['data']['market_cap_percentage']['btc']
        return btc_dominance
    except:
        return None

# Генерация текста отчёта
def generate_report(prices, spikes, dominance):
    now = datetime.now(pytz.timezone("Europe/Minsk")).strftime("%d.%m.%Y %H:%M")
    lines = [f"📊 *Криптоотчёт на {now}* (время Минск)\n"]

    lines.append("💰 *Текущие цены:*")
    for symbol in TOKENS:
        lines.append(f"{symbol}: ${prices[symbol]:,.2f}")

    if dominance is not None:
        lines.append(f"\n📈 Доминация BTC: {dominance:.2f}%")

    if spikes:
        lines.append("\n⚡ *Резкие движения цен:*")
        for entry in spikes:
            lines.append(entry)

    lines.append("\n⚠️ Это не финансовый совет.")
    return '\n'.join(lines)

# Отправка отчёта в Telegram
def send_to_telegram(text):
    requests.post(TELEGRAM_API, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

# Главная функция
def main():
    try:
        prices = fetch_current_prices()
        spikes = []
        for symbol in TOKENS:
            cid = COINGECKO_IDS[symbol]
            hist_4h = fetch_historical(cid, 4)
            change_4h = calculate_price_change(hist_4h)
            if abs(change_4h) >= 5:
                spikes.append(f"{symbol}: {change_4h:+.2f}% за 4ч")

            hist_1h = fetch_historical(cid, 1)
            change_1h = calculate_price_change(hist_1h)
            if abs(change_1h) >= 10:
                spikes.append(f"{symbol}: {change_1h:+.2f}% за 1ч")

        dominance = fetch_btc_dominance()
        report = generate_report(prices, spikes, dominance)
        send_to_telegram(report)
    except Exception as e:
        send_to_telegram(f"❌ Ошибка в отчёте: {str(e)}")

if __name__ == "__main__":
    main()
