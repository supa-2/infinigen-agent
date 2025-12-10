#!/bin/bash
# 安装依赖并启动开发服务器

source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen

cd /home/ubuntu/infinigen_web/infinigen-web-frontend

echo "=========================================="
echo "安装依赖..."
echo "=========================================="

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "node_modules 不存在，正在安装依赖..."
    npm install
else
    echo "node_modules 已存在，检查是否需要更新..."
    # 检查 vite 是否存在
    if [ ! -f "node_modules/.bin/vite" ]; then
        echo "vite 未找到，重新安装依赖..."
        npm install
    else
        echo "✅ 依赖已安装"
    fi
fi

echo ""
echo "=========================================="
echo "启动开发服务器..."
echo "=========================================="
echo "前端地址: http://localhost:5173"
echo "后端 API: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

npm run dev

