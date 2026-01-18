import asyncio
import os
import random
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import datetime

# 定义我们要抓取的资产列表
SYMBOLS = ["AAPL", "GOOGL", "MSFT", "BTC-USD", "ETH-USD", "EURUSD=X"]

# 模拟价格数据（用于演示，因为真实API可能被限流）
MOCK_PRICES = {
    "AAPL": 185.50,
    "GOOGL": 142.30,
    "MSFT": 378.90,
    "BTC-USD": 42500.00,
    "ETH-USD": 2280.50,
    "EURUSD=X": 1.0850
}

# 从环境变量获取数据库连接，如果没有则使用默认值（适配 Docker 环境）
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/economy_data")

async def fetch_and_insert():
    print(f"[{datetime.datetime.now()}] 开始采集数据...")
    print("注意：使用模拟数据（由于Yahoo Finance API限流）")

    data_to_insert = []
    current_time = datetime.datetime.now(datetime.timezone.utc)

    # 生成模拟市场数据
    for symbol in SYMBOLS:
        try:
            # 获取基础价格并添加微小随机波动
            base_price = MOCK_PRICES[symbol]
            # 添加 ±1% 的随机波动
            price = base_price * (1 + random.uniform(-0.01, 0.01))

            data_to_insert.append({
                "time": current_time,
                "symbol": symbol,
                "price": round(price, 2)
            })
            print(f"  -> 获取到 {symbol}: {price:.2f}")

        except Exception as e:
            print(f"  -> ❌ 获取 {symbol} 失败: {e}")

    if not data_to_insert:
        print("没有获取到任何数据，终止写入。")
        return

    # 2. 写入数据库
    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # 构建批量插入 SQL
            # 注意：TimescaleDB/Postgres 的 TIMESTAMPTZ 需要标准的 datetime 对象
            for item in data_to_insert:
                await conn.execute(
                    text("INSERT INTO market_ticks (time, symbol, price) VALUES (:time, :symbol, :price)"),
                    item
                )
            print(f"✅ 成功写入 {len(data_to_insert)} 条数据到 TimescaleDB")
    except Exception as e:
        print(f"❌ 数据库写入失败: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    # 运行异步任务
    asyncio.run(fetch_and_insert())
