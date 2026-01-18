#!/bin/bash

# AI 智能分析平台 - 快速启动脚本

set -e

echo "🚀 启动全球经济情报平台（含 AI 分析功能）"
echo "======================================"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件"
    echo "📝 正在创建 .env 模板..."

    cp .env.example .env
    echo ""
    echo "✅ 已创建 .env 文件"
    echo "⚠️  请编辑 .env 文件，填入你的 DEEPSEEK_API_KEY"
    echo ""
    echo "   1. 访问 https://platform.deepseek.com/ 获取 API Key"
    echo "   2. 编辑 .env 文件：DEEPSEEK_API_KEY=sk-your_key_here"
    echo "   3. 重新运行此脚本"
    echo ""
    exit 1
fi

# 检查 API Key 是否已配置
if grep -q "your_deepseek_api_key_here" .env 2>/dev/null || grep -q "^DEEPSEEK_API_KEY=$" .env 2>/dev/null; then
    echo "⚠️  DEEPSEEK_API_KEY 未配置"
    echo ""
    echo "   请编辑 .env 文件，填入你的 DeepSeek API Key："
    echo "   DEEPSEEK_API_KEY=sk-your_actual_key_here"
    echo ""
    exit 1
fi

echo "✅ 环境配置检查通过"
echo ""

# 启动服务
echo "🐳 启动 Docker 服务..."
docker compose up --build

# 如果需要后台运行，使用：
# docker compose up --build -d
# 然后查看日志：docker compose logs -f
