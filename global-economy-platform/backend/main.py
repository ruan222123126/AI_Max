from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

app = FastAPI()

# 从环境变量获取数据库连接串
DATABASE_URL = os.getenv("DATABASE_URL")

@app.on_event("startup")
async def startup_event():
    # 1. 连接数据库
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # 2. 创建一个测试表
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS market_ticks (
                time TIMESTAMPTZ NOT NULL,
                symbol TEXT NOT NULL,
                price DOUBLE PRECISION
            );
        """))

        # 3. 关键：将普通表转换为 TimescaleDB 的超表 (Hypertable)
        # 如果这步报错，说明 TimescaleDB 插件没加载成功
        try:
            await conn.execute(text("SELECT create_hypertable('market_ticks', 'time', if_not_exists => TRUE);"))
            print("成功创建 TimescaleDB 超表！")
        except Exception as e:
            print(f"超表创建失败: {e}")

@app.get("/")
async def root():
    return {"status": "System Operational", "message": "Global Economic Platform is active."}
