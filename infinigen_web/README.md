# Infinigen Web - 网页界面

这是一个连接 Infinigen Agent 的网页界面，允许用户通过网页生成室内场景、查看进度、下载生成的场景文件和渲染图片。

## 功能特性

- ✅ 通过网页界面生成室内场景
- ✅ 实时显示生成进度
- ✅ 展示生成的渲染图片
- ✅ 下载场景文件（.blend）和渲染图片
- ✅ 展示论文中的示例场景

## 项目结构

```
infinigen_web/
├── app.py              # Flask 后端API服务器
├── react               # React 前端代码
├── requirements.txt    # Python 依赖
└── README.md          # 本文件
```

## 安装和运行

### 1. 安装 Python 依赖

```bash
cd /home/ubuntu/infinigen_web
pip install -r requirements.txt
```

### 2. 启动后端服务器

```bash
python app.py
```

后端服务器将在 `http://localhost:5000` 启动。

### 3. 前端部署

React 前端代码需要编译和部署。你可以使用以下方式之一：

#### 方式1: 使用 Vite/Next.js 等构建工具

如果你有 React 开发环境，可以将 `react` 文件重命名为 `App.jsx` 或 `App.tsx`，然后使用相应的构建工具。

#### 方式2: 使用简单的 HTML 文件（推荐用于快速测试）

创建一个简单的 HTML 文件来加载 React（通过 CDN）：

```bash
# 创建 index.html（见下方示例）
```

#### 方式3: 使用 Node.js 和 React

```bash
# 安装依赖
npm install react react-dom

# 使用 webpack 或其他构建工具编译
```

## API 接口

### POST /api/generate
生成场景

**请求体:**
```json
{
  "request": "生成一个北欧风格的卧室",
  "seed": null  // 可选，随机种子
}
```

**响应:**
```json
{
  "task_id": "uuid",
  "status": "pending",
  "message": "任务已创建，正在生成场景..."
}
```

### GET /api/task/<task_id>/status
查询任务状态

**响应:**
```json
{
  "task_id": "uuid",
  "status": "running|completed|failed",
  "message": "状态消息",
  "progress": 45,
  "current_stage": "正在执行: solve_rooms",
  "rendered_image": "/path/to/image.png"  // 完成时
}
```

### GET /api/task/<task_id>/image
获取渲染图片（直接返回图片）

### GET /api/task/<task_id>/download/<file_type>
下载文件

- `file_type`: `scene` 或 `image`

### GET /api/tasks
列出所有任务

### GET /api/health
健康检查

## 使用示例

1. 打开网页界面
2. 点击 "Start AI Chat" 或 "Let's Talk"
3. 在聊天界面中输入场景描述，例如：
   - "生成一个北欧风格的卧室"
   - "生成一个现代风格的客厅，沙发是蓝色的"
4. 等待场景生成（通常需要 8-13 分钟）
5. 生成完成后，可以：
   - 查看渲染图片
   - 下载场景文件（.blend）
   - 下载渲染图片

## 注意事项

- 场景生成需要较长时间（8-13 分钟），请耐心等待
- 确保 Infinigen 环境已正确配置
- 后端服务器需要访问 `/home/ubuntu/infinigen` 目录
- 生成的场景文件保存在 `/home/ubuntu/infinigen/outputs/web_task_<task_id>/`

## 故障排除

### Agent 未初始化
如果看到 "Agent 未初始化" 错误，请检查：
- Infinigen 根目录路径是否正确（默认: `/home/ubuntu/infinigen`）
- 相关依赖是否已安装

### 前端无法连接后端
- 检查后端服务器是否正在运行
- 检查 `API_BASE_URL` 是否正确（默认: `http://localhost:5000/api`）
- 检查 CORS 设置

## 开发

### 修改 API 地址

在 `react` 文件中修改：
```javascript
const API_BASE_URL = 'http://your-api-url:5000/api';
```

### 添加新功能

- 后端：在 `app.py` 中添加新的路由
- 前端：在 `react` 文件中添加新的组件和功能

## 许可证

与 Infinigen 项目保持一致。

