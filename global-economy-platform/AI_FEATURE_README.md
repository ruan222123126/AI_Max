# AI 智能分析功能使用指南

## 🚀 功能概述

本系统现已集成 **AI 智能分析功能**，基于 DeepSeek 大语言模型，能够分析 TimescaleDB 中的市场数据并生成专业的财经简报。

### 核心特性

- ✅ **数据驱动分析**：基于真实的 24 小时市场数据
- ✅ **专业级报告**：生成华尔街风格的财经分析
- ✅ **实时交互**：点击按钮即可获取 AI 洞察
- ✅ **打字机效果**：优雅的结果展示体验

---

## 📋 前置准备

### 1. 获取 DeepSeek API Key

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册账号并登录
3. 进入 API Keys 页面创建新的密钥
4. 复制 API Key（格式：`sk-xxxxx`）

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
DEEPSEEK_API_KEY=sk-your_actual_api_key_here
```

---

## 🔧 启动系统

### 方式一：使用 Docker Compose（推荐）

```bash
# 1. 确保已配置 .env 文件
# 2. 启动所有服务
docker-compose up --build

# 3. 服务启动后，访问前端
# http://localhost:3000
```

### 方式二：手动启动

**后端：**
```bash
cd backend
pip install -r requirements.txt
export DEEPSEEK_API_KEY="sk-your_key_here"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**前端：**
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

---

## 💡 使用方法

### 通过 Web 界面

1. 打开浏览器访问 `http://localhost:3000`
2. 在顶部卡片中选择要分析的资产（如 BTC-USD）
3. 点击下方的 **"AI 智能分析"** 按钮
4. 等待几秒钟，AI 将生成专业的市场分析报告
5. 报告包含：
   - 市场概况
   - 技术分析
   - 波动性评估
   - 风险提示
   - 展望建议

### 通过 API 直接调用

```bash
curl -X POST http://localhost:8000/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USD"
  }'
```

**响应示例：**
```json
{
  "symbol": "BTC-USD",
  "analysis": "## 市场分析报告\n\n### 市场概况\nBTC-USD 在过去24小时内...",
  "generated_at": "2025-01-18T10:30:00.000Z"
}
```

---

## 🏗️ 技术架构

### 数据流

```
用户点击 "生成分析报告"
    ↓
前端发送 POST /api/ai/analyze
    ↓
FastAPI 接收请求
    ↓
查询 TimescaleDB 获取 24h 历史数据
    ↓
计算统计指标（最高/最低/波动率/趋势）
    ↓
构建 Prompt（数据 → 自然语言）
    ↓
调用 DeepSeek API
    ↓
AI 生成 Markdown 格式分析报告
    ↓
返回前端，打字机效果展示
```

### 核心文件

| 文件 | 作用 |
|------|------|
| `backend/ai_service.py` | AI 服务核心逻辑（数据查询、Prompt 构建） |
| `backend/main.py` | FastAPI 端点定义（`/ai/analyze`） |
| `frontend/app/page.tsx` | React 组件（UI 交互、打字机效果） |

---

## 🎯 AI 分析维度

AI 会分析以下指标：

1. **价格统计**
   - 最新价格、最高价、最低价
   - 平均价格、价格变化百分比

2. **技术指标**
   - 波动率（标准差）
   - 趋势判断（上涨/下跌/震荡）

3. **市场洞察**
   - 波动原因分析
   - 支撑位/阻力位评估
   - 风险提示

4. **投资建议**（不构成投资建议）
   - 观察要点
   - 需要关注的关键价位

---

## 🔍 故障排查

### 问题 1：点击按钮后一直显示"分析中..."

**可能原因：**
- API Key 未配置或无效
- 后端服务未启动
- 网络连接问题

**解决方案：**
```bash
# 检查后端日志
docker-compose logs backend

# 检查环境变量
docker-compose exec backend env | grep DEEPSEEK
```

### 问题 2：显示"AI 服务未配置"

**解决方案：**
确认 `.env` 文件存在且包含正确的 `DEEPSEEK_API_KEY`

### 问题 3：分析结果不准确

这是正常的！AI 的分析质量取决于：
- 数据量（需要至少 24 小时的数据）
- 市场波动性
- Prompt 工程的质量

你可以通过修改 `backend/ai_service.py` 中的 `build_analysis_prompt()` 函数来优化 AI 的输出。

---

## 🔮 未来扩展

### 可能的改进方向

1. **支持自定义问题**
   - 允许用户输入具体问题（如"现在的市场适合入场吗？"）
   - 多轮对话能力

2. **更多 AI 模型**
   - 支持 OpenAI GPT-4o
   - 支持 Claude 3.5 Sonnet
   - 模型切换功能

3. **高级分析功能**
   - 技术指标计算（RSI、MACD、布林带）
   - 多资产相关性分析
   - 新闻事件关联分析

4. **历史记录**
   - 保存历史分析记录
   - 对比不同时间点的分析结果

---

## 📊 成本估算

DeepSeek API 定价（仅供参考）：

| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| DeepSeek-V3 | ¥1/百万tokens | ¥2/百万tokens |

**单次分析成本估算：**
- 输入：约 500 tokens（数据 + Prompt）
- 输出：约 500 tokens（分析报告）
- **成本：约 ¥0.0015/次**

**结论：** 即使频繁使用，成本也非常低廉。

---

## 📝 开发笔记

### Prompt 工程最佳实践

1. **角色设定**：明确的专家身份（华尔街策略师）
2. **数据约束**：强调不要编造数据
3. **结构要求**：指定输出格式（Markdown、字数）
4. **语气把控**：专业但易懂，不过度自信

### 安全考虑

- ✅ AI 输出明确标注"不构成投资建议"
- ✅ 数据来源于真实数据库，不依赖 AI 的知识库
- ✅ API Key 通过环境变量管理，不硬编码

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个功能！

---

**Happy Trading! 🚀**
