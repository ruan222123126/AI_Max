from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

app = FastAPI(title="Global Economy Platform API")

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

# --- Pydantic 模型 (定义数据契约) ---
class MarketTick(BaseModel):
    time: datetime
    symbol: str
    price: float

    class Config:
        from_attributes = True

# --- 启动事件 ---
@app.on_event("startup")
async def startup_event():
    # 确保表结构存在 (与 Step 1 逻辑保持一致)
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS market_ticks (
                time TIMESTAMPTZ NOT NULL,
                symbol TEXT NOT NULL,
                price DOUBLE PRECISION
            );
        """))
        try:
            # 尝试转换为超表 (如果已存在会忽略警告)
            await conn.execute(text("SELECT create_hypertable('market_ticks', 'time', if_not_exists => TRUE);"))
        except Exception as e:
            print(f"TimescaleDB info: {e}")

# --- API 接口 ---

@app.get("/")
async def root():
    return {
        "status": "online",
        "endpoints": ["/market/latest", "/market/history/{symbol}"]
    }

@app.get("/market/latest", response_model=List[MarketTick])
async def get_latest_prices():
    """
    获取每个资产的最新一条价格数据。
    使用 Postgres 的 DISTINCT ON 语法高效去重。
    """
    async with engine.connect() as conn:
        # DISTINCT ON (symbol) 保证每个 symbol 只取第一条
        # ORDER BY symbol, time DESC 保证取到的是时间最新的一条
        query = text("""
            SELECT DISTINCT ON (symbol) time, symbol, price
            FROM market_ticks
            ORDER BY symbol, time DESC;
        """)
        result = await conn.execute(query)
        # 将数据库行转换为字典列表
        return [
            {"time": row.time, "symbol": row.symbol, "price": row.price}
            for row in result
        ]

@app.get("/market/history/{symbol}", response_model=List[MarketTick])
async def get_market_history(
    symbol: str,
    limit: int = Query(100, le=1000) # 默认100条,最大允许1000条
):
    """
    获取指定资产的历史价格数据,用于绘图。
    """
    async with engine.connect() as conn:
        query = text("""
            SELECT time, symbol, price
            FROM market_ticks
            WHERE symbol = :symbol
            ORDER BY time DESC
            LIMIT :limit;
        """)
        result = await conn.execute(query, {"symbol": symbol, "limit": limit})
        rows = result.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

        return [
            {"time": row.time, "symbol": row.symbol, "price": row.price}
            for row in rows
        ]
