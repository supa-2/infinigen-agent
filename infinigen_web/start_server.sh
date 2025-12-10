#!/bin/bash
# 启动 Infinigen Web 后端服务器

echo "=========================================="
echo "启动 Infinigen Web 后端服务器"
echo "=========================================="

cd /home/ubuntu/infinigen_web

# 检查 Python 依赖
echo "检查 Python 依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "安装 Python 依赖..."
    pip3 install -r requirements.txt
fi

# 启动服务器
echo "启动 Flask 服务器..."
echo "服务器地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

python3 app.py

