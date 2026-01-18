"""
AI 分析服务模块
负责从数据库获取市场数据，调用 LLM 生成智能分析报告
"""
from openai import AsyncOpenAI
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# 初始化 AI 客户端（支持 DeepSeek 和 OpenAI）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 使用 DeepSeek API（兼容 OpenAI SDK）
client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
) if DEEPSEEK_API_KEY else None


async def fetch_market_context(engine, symbol: str, hours: int = 24) -> Dict:
    """
    从数据库获取市场数据，构建 AI 分析的上下文

    Args:
        engine: 数据库引擎
        symbol: 资产代码（如 BTC-USD）
        hours: 查询过去几小时的数据

    Returns:
        包含统计信息的字典
    """
    async with engine.connect() as conn:
        # 查询指定时间范围内的数据
        query = text("""
            SELECT
                time,
                symbol,
                price,
                EXTRACT(EPOCH FROM (time - LAG(time) OVER (ORDER BY time))) as time_diff
            FROM market_ticks
            WHERE symbol = :symbol
              AND time > NOW() - INTERVAL ':hours hours'
            ORDER BY time DESC
            LIMIT 1000
        """)

        result = await conn.execute(
            text("""
                SELECT time, symbol, price
                FROM market_ticks
                WHERE symbol = :symbol
                  AND time > NOW() - INTERVAL '1 day'
                ORDER BY time DESC
                LIMIT 1000
            """),
            {"symbol": symbol}
        )
        rows = result.fetchall()

        if not rows:
            return None

        prices = [row.price for row in rows]
        times = [row.time for row in rows]

        # 计算统计指标
        current_price = prices[0]
        highest = max(prices)
        lowest = min(prices)
        avg_price = sum(prices) / len(prices)

        # 计算价格变化
        price_change = prices[0] - prices[-1] if len(prices) > 1 else 0
        price_change_pct = (price_change / prices[-1] * 100) if prices[-1] != 0 else 0

        # 计算波动率（标准差）
        variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
        volatility = variance ** 0.5

        # 判断趋势
        if price_change_pct > 2:
            trend = "强势上涨"
        elif price_change_pct > 0.5:
            trend = "温和上涨"
        elif price_change_pct > -0.5:
            trend = "震荡整理"
        elif price_change_pct > -2:
            trend = "温和下跌"
        else:
            trend = "强势下跌"

        # 查询最近 5 条新闻
        news_query = text("SELECT title, source, published_at FROM financial_news ORDER BY published_at DESC LIMIT 5;")
        news_result = await conn.execute(news_query)
        news_rows = news_result.fetchall()
        news_titles = [{"title": row.title, "source": row.source, "published_at": row.published_at} for row in news_rows]

        return {
            "symbol": symbol,
            "current_price": current_price,
            "highest": highest,
            "lowest": lowest,
            "avg_price": avg_price,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "volatility": volatility,
            "trend": trend,
            "data_points": len(prices),
            "time_range": "过去24小时",
            "recent_news": news_titles
        }


def build_analysis_prompt(context: Dict) -> str:
    """
    构建 AI 分析的 Prompt

    Args:
        context: 市场数据上下文

    Returns:
        完整的 prompt 字符串
    """
    system_instruction = """你是一位专业的华尔街宏观策略师和金融分析师。

你的任务是根据提供的真实市场数据和最新新闻，撰写一份简明、专业的财经简报。

请遵循以下原则：
1. **数据驱动**：仅基于提供的数据进行分析，不要编造数据
2. **专业视角**：使用金融专业术语，但要保持清晰易懂
3. **洞察深刻**：不仅描述"发生了什么"，更要分析"意味着什么"
4. **结构清晰**：使用 Markdown 格式，包含市场概况、技术分析、风险提示等部分
5. **行动导向**：在适当的情况下提供观察和展望（不构成投资建议）
6. **新闻感知**：结合最新市场新闻分析价格波动的原因

输出格式要求：
- 使用 Markdown 格式
- 总字数控制在 300-500 字
- 使用emoji图标增强可读性
- 重点内容使用加粗标注"""

    # 构建新闻上下文
    news_section = ""
    if context.get('recent_news') and len(context['recent_news']) > 0:
        news_items = []
        for news in context['recent_news'][:5]:
            news_items.append(f"- **{news['title']}** ({news['source']})")
        news_section = f"""
### 最新市场新闻
{chr(10).join(news_items)}
"""

    user_data = f"""
## 市场数据

**资产代码**: {context['symbol']}
**时间范围**: {context['time_range']}

### 价格统计
- **最新价**: ${context['current_price']:,.2f}
- **期间最高**: ${context['highest']:,.2f}
- **期间最低**: ${context['lowest']:,.2f}
- **平均价格**: ${context['avg_price']:,.2f}

### 波动分析
- **价格变化**: ${context['price_change']:+,.2f} ({context['price_change_pct']:+.2f}%)
- **波动率**: {context['volatility']:.2f}
- **趋势判断**: {context['trend']}
- **数据点数**: {context['data_points']} 个

{news_section}
请基于以上价格数据和新闻标题，综合分析市场走势和可能的驱动因素，为投资者撰写一份专业的市场分析简报。
"""

    return f"{system_instruction}\n\n{user_data}"


async def generate_market_analysis(engine, symbol: str) -> Optional[str]:
    """
    生成市场分析报告的主函数

    Args:
        engine: 数据库引擎
        symbol: 资产代码

    Returns:
        AI 生成的分析报告（Markdown 格式），如果出错返回 None
    """
    if not client:
        return "⚠️ AI 服务未配置：请设置 DEEPSEEK_API_KEY 环境变量"

    try:
        # 1. 获取市场数据上下文
        context = await fetch_market_context(engine, symbol)
        if not context:
            return f"⚠️ 未找到 {symbol} 的市场数据，请确认资产代码正确或数据已采集"

        # 2. 构建 Prompt
        prompt = build_analysis_prompt(context)

        # 3. 调用 LLM 生成分析
        response = await client.chat.completions.create(
            model="deepseek-chat",  # 使用 DeepSeek V3 模型
            messages=[
                {"role": "system", "content": "你是一位专业的华尔街宏观策略师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # 适中的创造性
            max_tokens=1000,  # 控制输出长度
        )

        analysis = response.choices[0].message.content

        # 添加数据时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"{analysis}\n\n---\n*📊 分析基于 {context['time_range']} 数据 | 生成时间: {timestamp}*"

    except Exception as e:
        return f"❌ AI 分析出错：{str(e)}"
