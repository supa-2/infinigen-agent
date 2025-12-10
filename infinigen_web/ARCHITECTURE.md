# 系统架构说明

## 概述

Infinigen Web 是一个连接 Infinigen Agent 的网页界面系统，允许用户通过网页生成室内场景、查看进度、下载生成的场景文件和渲染图片。

## 系统架构

```
┌─────────────────┐
│   Web Browser   │  (React 前端)
│   (React App)   │
└────────┬────────┘
         │ HTTP/API
         │
┌────────▼────────┐
│  Flask Backend  │  (app.py)
│   (API Server)  │
└────────┬────────┘
         │
┌────────▼────────┐
│ Infinigen Agent │  (infinigen_agent)
│  (Scene Gen)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  Infinigen Core │  (Blender)
│  (Rendering)    │
└─────────────────┘
```

## 组件说明

### 1. 前端 (React)

**文件**: `react`

**功能**:
- 用户界面展示
- 与后端 API 通信
- 实时显示生成进度
- 展示生成的图片
- 提供文件下载功能

**主要组件**:
- `ChatInterface`: AI 聊天界面，用于输入场景描述
- `Navbar`: 导航栏
- `Hero`: 首页英雄区域
- `Portfolio`: 展示论文示例场景
- `Features`: 功能特性介绍

**API 调用**:
- `POST /api/generate`: 创建生成任务
- `GET /api/task/<task_id>/status`: 查询任务状态（轮询）
- `GET /api/task/<task_id>/image`: 获取渲染图片
- `GET /api/task/<task_id>/download/<file_type>`: 下载文件

### 2. 后端 (Flask)

**文件**: `app.py`

**功能**:
- 接收前端请求
- 调用 Infinigen Agent 生成场景
- 管理任务状态
- 提供文件下载服务
- 进度监控

**主要接口**:
- `POST /api/generate`: 创建生成任务
- `GET /api/task/<task_id>/status`: 查询任务状态
- `GET /api/task/<task_id>/image`: 获取渲染图片
- `GET /api/task/<task_id>/download/<file_type>`: 下载文件
- `GET /api/tasks`: 列出所有任务
- `GET /api/health`: 健康检查

**任务状态管理**:
- `pending`: 任务已创建，等待执行
- `running`: 任务正在执行
- `completed`: 任务完成
- `failed`: 任务失败

### 3. Infinigen Agent

**位置**: `/home/ubuntu/infinigen/infinigen_agent`

**功能**:
- 场景生成
- 颜色应用
- 场景渲染

**调用流程**:
1. `process_request_with_auto_generate()`: 完整流程
   - 生成场景
   - 应用颜色
   - 渲染图片

## 数据流

### 场景生成流程

```
用户输入
  ↓
前端发送 POST /api/generate
  ↓
后端创建任务 (task_id)
  ↓
后台线程启动生成任务
  ↓
调用 agent.process_request_with_auto_generate()
  ↓
  ├─ 生成场景 (generate_scene_from_request)
  ├─ 应用颜色 (process_request)
  └─ 渲染图片 (render_scene_image)
  ↓
更新任务状态为 completed
  ↓
前端轮询获取状态
  ↓
显示生成的图片和下载链接
```

### 进度监控流程

```
后端任务执行中
  ↓
定期更新任务状态 (progress, current_stage)
  ↓
前端每 2 秒轮询 GET /api/task/<task_id>/status
  ↓
更新 UI 显示进度条和当前阶段
```

## 文件存储

生成的场景文件存储在：
```
/home/ubuntu/infinigen/outputs/web_task_<task_id>/
├── scene.blend              # 原始场景
├── scene_colored.blend      # 应用颜色后的场景
├── pipeline_coarse.csv      # 生成进度记录
└── frames/                  # 渲染图片
    └── Image/
        └── camera_0/
            └── Image_0_0_0001_0.png
```

## 配置

### 后端配置

在 `app.py` 中：
- `UPLOAD_FOLDER`: 输出目录（默认: `/home/ubuntu/infinigen/outputs`）
- `API_BASE_URL`: API 基础地址（前端使用）

### 前端配置

在 `react` 文件中：
- `API_BASE_URL`: 后端 API 地址（默认: `http://localhost:5000/api`）

## 安全考虑

1. **CORS**: 已启用 CORS，允许跨域请求
2. **文件下载**: 使用 Flask 的 `send_file`，确保安全
3. **任务隔离**: 每个任务使用独立的目录
4. **输入验证**: 前端和后端都应验证用户输入

## 扩展建议

1. **用户认证**: 添加用户登录和权限管理
2. **任务队列**: 使用 Celery 等任务队列系统处理长时间任务
3. **数据库**: 使用数据库存储任务历史和用户数据
4. **WebSocket**: 使用 WebSocket 实现实时进度推送（替代轮询）
5. **缓存**: 添加 Redis 缓存常用数据
6. **负载均衡**: 多实例部署时使用负载均衡

## 性能优化

1. **异步处理**: 场景生成在后台线程执行，不阻塞 API
2. **进度缓存**: 缓存任务状态，减少文件读取
3. **图片压缩**: 大图片可以压缩后传输
4. **CDN**: 静态资源使用 CDN 加速

