import asyncio
import os
import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# RSS 源列表
RSS_URLS = [
    "https://finance.yahoo.com/news/rssindex",
]

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/economy_data")

async def fetch_news():
    print(f"[{datetime.now()}] 正在扫描全球财经新闻...")

    engine = create_async_engine(DATABASE_URL, echo=False)
    news_items = []

    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            print(f"  -> 从 {url} 获取到 {len(feed.entries)} 条新闻")

            for entry in feed.entries[:5]:
                # 解析时间
                if hasattr(entry, 'published'):
                    pub_date = parsedate_to_datetime(entry.published)
                else:
                    pub_date = datetime.now()

                news_items.append({
                    "published_at": pub_date,
                    "title": entry.title,
                    "source": "Yahoo Finance",
                    "url": entry.link,
                    "sentiment_score": 0.0
                })
        except Exception as e:
            print(f"  ❌ RSS 解析失败: {e}")

    # 写入数据库
    async with engine.begin() as conn:
        for item in news_items:
            try:
                await conn.execute(text("""
                    INSERT INTO financial_news (published_at, title, source, url, sentiment_score)
                    VALUES (:published_at, :title, :source, :url, :sentiment_score)
                    ON CONFLICT (url) DO NOTHING;
                """), item)
            except Exception as e:
                print(f"写入错误: {e}")

    print(f"✅ 新闻入库完成")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fetch_news())
