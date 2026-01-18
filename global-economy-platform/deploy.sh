#!/bin/bash

echo "🚀 开始部署 Global Economy Platform..."

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在，请先创建并配置环境变量"
    echo "💡 提示: 可以参考 .env.example 文件创建 .env"
    exit 1
fi

# 1. 停止旧容器
echo "🛑 停止旧容器..."
docker compose down

# 2. 拉取最新代码 (如果你用了 git，取消下面的注释)
# git pull origin main

# 3. 重新构建并启动 (后台模式)
# --build 确保使用了最新的代码和 .env 变量
echo "🔨 重新构建并启动服务..."
docker compose up -d --build

echo "✅ 系统已在后台启动！"
echo "📊 前端访问: http://localhost:3000"
echo "🔌 后端 API: http://localhost:8000/docs"
echo "📝 查看日志: docker compose logs -f"
echo "🛑 停止服务: docker compose down"
