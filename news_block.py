import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def fetch_news():
    try:
        url = "https://cryptopanic.com/api/v1/posts/?auth_token=demo&public=true"
        res = requests.get(url)
        items = res.json().get("results", [])
        news = []
        for item in items:
            title = item.get("title", "")
            if title:
                news.append(f"— {title}")
            if len(news) == 3:
                break
        return news
    except Exception:
        return ["Новости недоступны"]

def build_news_block():
    news = fetch_news()
    if news and any(n for n in news if "недоступны" not in n):
        lines = ["📰 *Свежие новости и сигналы:*"]
        lines += news
    else:
        lines = ["📰 Новости недоступны"]
    return "\n".join(lines)

def send_news_block():
    news_block = build_news_block()
    requests.post(TG_API, data={
        "chat_id": CHAT_ID,
        "text": news_block,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    send_news_block()
