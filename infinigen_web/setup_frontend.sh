#!/bin/bash
# 在 infinigen conda 环境下设置前端项目

source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen

cd /home/ubuntu/infinigen_web

echo "=========================================="
echo "步骤 1: 创建 Vite React 项目"
echo "=========================================="

# 如果项目已存在，先删除
if [ -d "infinigen-web-frontend" ]; then
    echo "项目已存在，删除旧项目..."
    rm -rf infinigen-web-frontend
fi

# 创建项目
npm create vite@latest infinigen-web-frontend -- --template react

cd infinigen-web-frontend

echo ""
echo "=========================================="
echo "步骤 2: 安装基础依赖"
echo "=========================================="
npm install

echo ""
echo "=========================================="
echo "步骤 3: 安装 Lucide React 图标库"
echo "=========================================="
npm install lucide-react

echo ""
echo "=========================================="
echo "步骤 4: 安装和配置 Tailwind CSS"
echo "=========================================="
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

echo ""
echo "=========================================="
echo "步骤 5: 配置 Tailwind"
echo "=========================================="

# 更新 tailwind.config.js
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# 更新 src/index.css
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

echo ""
echo "=========================================="
echo "步骤 6: 复制 App.jsx"
echo "=========================================="
cp ../App.jsx src/App.jsx

echo ""
echo "=========================================="
echo "✅ 项目设置完成！"
echo "=========================================="
echo ""
echo "下一步：运行 'npm run dev' 启动开发服务器"
echo ""

