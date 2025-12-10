#!/bin/bash
# 修复依赖安装问题

source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen

cd /home/ubuntu/infinigen_web/infinigen-web-frontend

echo "=========================================="
echo "诊断和修复依赖问题"
echo "=========================================="
echo ""

echo "1. 检查当前目录:"
pwd
echo ""

echo "2. 检查 npm 版本:"
npm --version
echo ""

echo "3. 检查 node 版本:"
node --version
echo ""

echo "4. 检查 package.json:"
cat package.json
echo ""

echo "5. 删除旧的 node_modules 和 lock 文件:"
rm -rf node_modules package-lock.json
echo ""

echo "6. 清理 npm 缓存:"
npm cache clean --force
echo ""

echo "7. 重新安装依赖:"
npm install --verbose 2>&1 | tail -30
echo ""

echo "8. 检查 vite 是否安装成功:"
if [ -f "node_modules/.bin/vite" ]; then
    echo "✅ vite 已安装"
    ls -lh node_modules/.bin/vite
else
    echo "❌ vite 未找到"
fi
echo ""

echo "9. 尝试使用 npx 运行 vite:"
npx vite --version
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="

