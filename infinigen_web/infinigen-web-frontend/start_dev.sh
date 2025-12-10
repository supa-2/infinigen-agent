#!/bin/bash
# 启动前端开发服务器

source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen

cd /home/ubuntu/infinigen_web/infinigen-web-frontend

echo "=========================================="
echo "启动 Infinigen Web 前端开发服务器"
echo "=========================================="
echo ""
echo "前端地址: http://localhost:5173"
echo "后端 API: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

# 使用 npx 运行 vite，确保能找到命令
npx vite

