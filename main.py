import os
import requests

from prices_report import build_prices_block
from forecast_block import build_forecast_block
from levels_block import build_levels_block
from btc_dominance_block import build_btc_dominance_block
from news_block import build_news_block
from jumps_block import build_jumps_block
from liquidation_levels_block import build_liquidation_levels_block

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def main():
    blocks = [
        build_prices_block(),
        build_forecast_block(),
        build_levels_block(),
        build_btc_dominance_block(),
        build_news_block(),
        build_jumps_block(),
        build_liquidation_levels_block(),
    ]
    full_report = "\n\n".join(blocks)
    resp = requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": full_report,
        "parse_mode": "Markdown"
    })
    print(resp.text)  # Покажи это в логе, чтобы видеть ошибки Telegram

if __name__ == "__main__":
    main()
