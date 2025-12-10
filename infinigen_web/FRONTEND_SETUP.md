# 前端项目设置完成 ✅

## 项目位置
```
/home/ubuntu/infinigen_web/infinigen-web-frontend/
```

## 已完成的配置

1. ✅ 创建了 Vite React 项目结构
2. ✅ 安装了所有依赖（React, Vite, Lucide React, Tailwind CSS）
3. ✅ 配置了 Tailwind CSS
4. ✅ 复制了 App.jsx 到项目中
5. ✅ 创建了所有必要的配置文件

## 启动项目

### 方法 1: 使用启动脚本（推荐）
```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen
cd /home/ubuntu/infinigen_web/infinigen-web-frontend
./start_dev.sh
```

### 方法 2: 直接运行
```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate infinigen
cd /home/ubuntu/infinigen_web/infinigen-web-frontend
npm run dev
```

## 访问地址

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:5000

## 注意事项

1. 确保后端服务器已启动（运行 `python3 app.py`）
2. 前端和后端需要在不同的终端窗口运行
3. 如果端口被占用，Vite 会自动选择其他端口

## 项目结构

```
infinigen-web-frontend/
├── src/
│   ├── App.jsx          # 主应用组件
│   ├── main.jsx        # 入口文件
│   └── index.css       # Tailwind CSS
├── public/             # 静态资源
├── index.html          # HTML 模板
├── vite.config.js      # Vite 配置
├── tailwind.config.js  # Tailwind 配置
├── postcss.config.js  # PostCSS 配置
├── package.json        # 项目配置
└── start_dev.sh        # 启动脚本
```

## 下一步

1. 启动后端服务器（在另一个终端）:
   ```bash
   cd /home/ubuntu/infinigen_web
   python3 app.py
   ```

2. 启动前端开发服务器:
   ```bash
   cd /home/ubuntu/infinigen_web/infinigen-web-frontend
   ./start_dev.sh
   ```

3. 打开浏览器访问 http://localhost:5173

