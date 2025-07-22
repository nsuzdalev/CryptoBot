import os
import requests
from datetime import datetime
import pytz

# === Настройки ===
TOKENS = ['BTC', 'ETH', 'ARB', 'SOL', 'APT', 'DOT', 'W', 'HFT', 'LTC', 'ATOM', 'ONDO']
CHAT_ID = os.getenv("CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CMC_API_KEY = os.getenv("CMC_API_KEY")  # Твой ключ от CoinMarketCap (если будешь использовать)
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# === Получение цен с CoinGecko (не требует ключа) ===
def fetch_prices():
    ids_map = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'ARB': 'arbitrum', 'SOL': 'solana',
        'APT': 'aptos', 'DOT': 'polkadot', 'W': 'wormhole', 'HFT': 'hashflow',
        'LTC': 'litecoin', 'ATOM': 'cosmos', 'ONDO': 'ondo-finance'
    }
    ids = ','.join(ids_map[token] for token in TOKENS)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    res = requests.get(url)
    data = res.json()
    return {token: data[ids_map[token]]['usd'] for token in TOKENS}

# === Генерация текста отчёта ===
def generate_report(prices: dict) -> str:
    now = datetime.now(pytz.timezone("Europe/Minsk")).strftime("%d.%m.%Y %H:%M")
    lines = [f"📊 Криптоотчёт на {now} (время Минск)
"]
    for token in TOKENS:
        lines.append(f"{token}: ${prices[token]:,.2f}")
    lines.append("
ℹ️ Прогноз, доминация, уровни ликвидации и скачки цен в полной версии (в разработке).")
    lines.append("
⚠️ Это не финансовый совет.")
    return '\n'.join(lines)

# === Отправка в Telegram ===
def send_to_telegram(text: str):
    requests.post(TELEGRAM_API, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

# === Главная функция ===
def main():
    try:
        prices = fetch_prices()
        report = generate_report(prices)
        send_to_telegram(report)
    except Exception as e:
        send_to_telegram(f"❌ Ошибка при формировании отчёта: {str(e)}")

if __name__ == "__main__":
    main()
