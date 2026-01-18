from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scripts.ingest_market_data import fetch_and_insert
from scripts.ingest_news import fetch_news
import datetime
import sys

# 创建异步调度器实例
scheduler = AsyncIOScheduler()

def start_scheduler():
    """
    启动定时任务
    """
    # 每 60 秒执行一次 fetch_and_insert
    # distinct_id 防止任务重叠
    scheduler.add_job(
        fetch_and_insert,
        trigger=IntervalTrigger(seconds=60),
        id='market_data_ingestion',
        name='Ingest Market Data',
        replace_existing=True
    )

    # 新闻采集任务：每 5 分钟 (300秒) 执行一次
    scheduler.add_job(
        fetch_news,
        trigger=IntervalTrigger(seconds=300),
        id='news_ingestion',
        name='Ingest Global News',
        replace_existing=True
    )

    scheduler.start()
    message = f"[{datetime.datetime.now()}] ✅ 自动化调度器已启动：每60秒采集一次市场数据，每5分钟采集一次新闻"
    print(message, flush=True)
    sys.stdout.flush()

def shutdown_scheduler():
    """
    关闭调度器
    """
    scheduler.shutdown()
    print("🛑 自动化调度器已关闭", flush=True)
    sys.stdout.flush()
