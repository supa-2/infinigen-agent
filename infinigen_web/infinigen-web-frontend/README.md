# Infinigen Web Frontend

## 问题修复

如果遇到 `vite: not found` 错误，请按以下步骤操作：

### 方法 1: 使用 npx（推荐）

直接使用 `npx vite` 而不是 `npm run dev`：

```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen
cd /home/ubuntu/infinigen_web/infinigen-web-frontend
npx vite
```

### 方法 2: 重新安装依赖

```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen
cd /home/ubuntu/infinigen_web/infinigen-web-frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### 方法 3: 全局安装 vite（不推荐）

```bash
npm install -g vite
```

## 启动项目

```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen
cd /home/ubuntu/infinigen_web/infinigen-web-frontend
npx vite
```

访问: http://localhost:5173

