# 快速启动指南

## 1. 启动后端服务器

```bash
cd /home/ubuntu/infinigen_web
./start_server.sh
```

或者直接运行：

```bash
python3 app.py
```

后端服务器将在 `http://localhost:5000` 启动。

## 2. 前端部署

### 选项 A: 使用 React 开发环境（推荐）

如果你有 Node.js 和 React 开发环境：

1. 将 `react` 文件重命名为 `App.jsx`
2. 创建 React 项目或将其集成到现有项目中
3. 安装依赖：`npm install react react-dom lucide-react`
4. 启动开发服务器

### 选项 B: 使用 Vite（快速）

```bash
# 安装 Vite
npm create vite@latest infinigen-web -- --template react

# 将 react 文件内容复制到 src/App.jsx
# 安装依赖
npm install lucide-react

# 启动开发服务器
npm run dev
```

### 选项 C: 使用 Create React App

```bash
npx create-react-app infinigen-web
# 将 react 文件内容复制到 src/App.js
# 安装依赖
npm install lucide-react
# 启动
npm start
```

## 3. 配置 API 地址

在前端代码中，确保 `API_BASE_URL` 指向正确的后端地址：

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

如果前端和后端不在同一台机器上，请修改为实际的后端地址。

## 4. 测试

1. 打开网页界面
2. 点击 "Start AI Chat" 或 "Let's Talk"
3. 输入场景描述，例如："生成一个北欧风格的卧室"
4. 等待场景生成（8-13 分钟）
5. 查看生成的图片和下载文件

## 故障排除

### 后端无法启动

- 检查 Python 版本（需要 Python 3.7+）
- 检查依赖是否安装：`pip install -r requirements.txt`
- 检查 Infinigen 路径是否正确

### 前端无法连接后端

- 检查后端是否正在运行
- 检查 `API_BASE_URL` 是否正确
- 检查浏览器控制台是否有 CORS 错误
- 如果使用 HTTPS，确保后端也支持 HTTPS 或配置代理

### 场景生成失败

- 检查 Infinigen 环境是否正确配置
- 检查输出目录权限
- 查看后端日志获取详细错误信息

## 开发提示

- 后端日志会显示详细的生成进度
- 任务状态可以通过 `/api/task/<task_id>/status` 查询
- 生成的场景文件保存在 `/home/ubuntu/infinigen/outputs/web_task_<task_id>/`

