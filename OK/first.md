这是一个非常宏大且架构严谨的项目规划。面对这样一个全栈（Full Stack）且包含 AI 的复杂系统，最忌讳的是“全面铺开”。

**第一步的核心目标应该是：打通“数据血液循环”。**

不需要做前端页面，不需要写复杂的 AI Prompt，甚至不需要抓取真实数据。第一步只需要验证 **FastAPI (后端) + TimescaleDB (数据库) + Docker (环境)** 这三者能协同工作。

以下是具体的、可执行的“第一步”实战指南：

### 第一步：搭建“最小可行性基础设施” (Infrastructure MVP)

我们先构建项目的骨架（Monorepo），并让数据库和后端跑起来。

#### 1. 初始化项目目录结构

在你的终端中执行以下命令，建立清晰的 Monorepo 结构：

```bash
mkdir global-economy-platform
cd global-economy-platform
mkdir backend frontend data
touch docker-compose.yml

```

#### 2. 编写 Docker 编排文件 (核心)

这是整个系统的基石。我们需要先配置 TimescaleDB，因为它比普通 Postgres 更复杂。
打开 `docker-compose.yml`，写入以下内容：

```yaml
version: '3.8'

services:
  # 1. 核心数据库：TimescaleDB (基于 Postgres)
  db:
    image: timescale/timescaledb:latest-pg15
    container_name: economy_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: economy_data
    ports:
      - "5432:5432"
    volumes:
      - ./data/postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d economy_data"]
      interval: 5s
      timeout: 5s
      retries: 5

  # 2. 后端 API：FastAPI
  backend:
    build: ./backend
    container_name: economy_backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/economy_data
    depends_on:
      db:
        condition: service_healthy

```

#### 3. 搭建最简后端 (Backend Skeleton)

进入 `backend` 目录，我们需要验证 FastAPI 能否连接到数据库并创建超表（Hypertable）。

**3.1 创建 `backend/Dockerfile**`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

```

**3.2 创建 `backend/requirements.txt**`

```text
fastapi
uvicorn
asyncpg
sqlalchemy

```

**3.3 创建 `backend/main.py` (验证代码)**
这段代码不仅启动服务器，还会在启动时自动创建一个 TimescaleDB 的超表，这是验证数据库选型是否成功的关键。

```python
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
            print("✅ 成功创建 TimescaleDB 超表！")
        except Exception as e:
            print(f"❌ 超表创建失败: {e}")

@app.get("/")
async def root():
    return {"status": "System Operational", "message": "Global Economic Platform is active."}

```

#### 4. 启动并验证

现在，让我们点火测试。

1. **启动容器：**
```bash
docker-compose up --build

```


2. **观察日志：**
你需要密切关注终端输出。如果看到 `✅ 成功创建 TimescaleDB 超表！`，恭喜你，最难的数据库环境配置已经完成了。
3. **API 测试：**
打开浏览器访问 `http://localhost:8000`。如果看到 JSON 返回 `{"status": "System Operational" ...}`，说明 Python 后端与 Docker 网络通信正常。
