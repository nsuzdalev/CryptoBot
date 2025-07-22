import requests
import time
import os

def fetch_news(retries=3):
    url = "https://cryptopanic.com/api/v1/posts/?auth_token=demo&public=true"
    for _ in range(retries):
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                items = res.json().get("results", [])
                news = []
                for item in items:
                    title = item.get("title", "")
                    if title:
                        news.append(f"— {title}")
                    if len(news) == 3:
                        break
                if news:
                    return news
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None

def build_news_block():
    news = fetch_news()
    if news:
        lines = ["📰 *Свежие новости и сигналы:*"]
        lines += news
    else:
        lines = ["📰 Новости недоступны (лимит API или нет связи с сервисом)"]
    return "\n".join(lines)

# Отправка блока в Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

if __name__ == "__main__":
    block = build_news_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": block,
        "parse_mode": "Markdown"
    })
