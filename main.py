import asyncio
import requests
from telegram import Bot
from deep_translator import GoogleTranslator

# --- CONFIG ---
API_KEY_NEWS = "c09d91931a424c518822f9b4a997e4c5"
CHAT_ID = "-1002631457012"
BOT_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"

bot = Bot(token=BOT_TOKEN)

# Simpan berita yang sudah pernah dikirim
sent_articles = set()

# Fungsi ambil berita terbaru
def get_news():
    url = f"https://newsapi.org/v2/everything?q=gold OR XAUUSD&apiKey={API_KEY_NEWS}&pageSize=5&sortBy=publishedAt"
    response = requests.get(url)
    data = response.json()
    return data.get("articles", [])

# Analisis dampak berita ke XAU/USD
def analyze_impact(title, description):
    impact_keywords = {
        "high": ["inflation", "interest rate", "federal reserve", "gold rally"],
        "medium": ["GDP", "unemployment", "economic growth"],
        "low": ["market update", "commodity", "dollar"]
    }
    score = 0
    text = f"{title} {description}".lower()
    for level, keywords in impact_keywords.items():
        for kw in keywords:
            if kw.lower() in text:
                if level == "high":
                    score += 3
                elif level == "medium":
                    score += 2
                else:
                    score += 1
    percent = min(int(score / 10 * 100), 100)
    return percent

# Tentukan rekomendasi buy/sell
def recommend_action(percent):
    if percent >= 60:
        return "SELL"
    elif percent >= 30:
        return "BUY"
    else:
        return "HOLD"

# Kirim berita ke Telegram (hanya yang relevan)
async def send_news():
    global sent_articles
    articles = get_news()
    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "")
        desc = article.get("description", "")

        if not url or url in sent_articles:  # skip jika sudah dikirim
            continue

        percent = analyze_impact(title, desc)

        # ⛔ Filter: hanya kirim kalau impact > 0
        if percent == 0:
            continue

        # Translate ke bahasa Indonesia
        title_id = GoogleTranslator(source='auto', target='id').translate(title or "")
        desc_id = GoogleTranslator(source='auto', target='id').translate(desc or "")

        action = recommend_action(percent)
        text = f"{title_id}\n{desc_id}\nImpact: {percent}%\nRecommendation: {action}\n\nSumber: {url}"

        await bot.send_message(chat_id=CHAT_ID, text=text)
        sent_articles.add(url)  # tandai sudah dikirim
        await asyncio.sleep(1)  # delay supaya tidak spam

# Main loop (cek terus tiap 30 detik, kirim hanya kalau ada berita baru & relevan)
async def main():
    while True:
        await send_news()
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
