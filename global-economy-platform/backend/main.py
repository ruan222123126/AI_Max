from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

# 导入 AI 服务模块
from ai_service import generate_market_analysis
# 导入调度器
from scheduler import start_scheduler, shutdown_scheduler

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

class FinancialNews(BaseModel):
    id: int
    published_at: datetime
    title: str
    source: str
    url: str
    sentiment_score: float

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

    # 2. 创建新闻表
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS financial_news (
                id SERIAL PRIMARY KEY,
                published_at TIMESTAMPTZ NOT NULL,
                title TEXT NOT NULL,
                source TEXT,
                url TEXT UNIQUE,
                sentiment_score FLOAT
            );
        """))

    # 启动自动化任务
    start_scheduler()

# --- API 接口 ---

@app.get("/")
async def root():
    return {
        "status": "online",
        "endpoints": [
            "/market/latest",
            "/market/history/{symbol}",
            "/ai/analyze",
            "/news/latest"
        ]
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


@app.get("/news/latest", response_model=List[FinancialNews])
async def get_latest_news(limit: int = Query(20, le=100)):
    """
    获取最新的财经新闻
    """
    async with engine.connect() as conn:
        query = text("""
            SELECT id, published_at, title, source, url, sentiment_score
            FROM financial_news
            ORDER BY published_at DESC
            LIMIT :limit;
        """)
        result = await conn.execute(query, {"limit": limit})
        return [
            {
                "id": row.id,
                "published_at": row.published_at,
                "title": row.title,
                "source": row.source,
                "url": row.url,
                "sentiment_score": row.sentiment_score
            }
            for row in result
        ]


# --- AI 分析接口 ---

class AnalysisRequest(BaseModel):
    symbol: str
    custom_question: Optional[str] = None


class AnalysisResponse(BaseModel):
    symbol: str
    analysis: str
    generated_at: datetime


@app.post("/ai/analyze", response_model=AnalysisResponse)
async def analyze_market(request: AnalysisRequest):
    """
    AI 智能市场分析接口

    基于 TimescaleDB 的历史数据，使用 DeepSeek LLM 生成专业的财经分析报告。

    Args:
        request: 包含 symbol（资产代码）和可选的 custom_question（自定义问题）

    Returns:
        AI 生成的分析报告

    Example:
        POST /ai/analyze
        {
            "symbol": "BTC-USD",
            "custom_question": "现在的市场适合入场吗？"
        }
    """
    # 调用 AI 服务生成分析
    analysis = await generate_market_analysis(engine, request.symbol)

    return {
        "symbol": request.symbol,
        "analysis": analysis,
        "generated_at": datetime.utcnow()
    }

# --- 关闭事件 ---
@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()

