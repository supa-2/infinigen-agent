# LangChain Infinigen Agent 使用指南

## 快速开始

### 方式 1: 直接运行主脚本（推荐）

```bash
cd /home/ubuntu/infinigen/infinigen_agent

# 交互式模式（推荐）
python src/langchain_agent.py

# 命令行模式
python src/langchain_agent.py "生成一个北欧风格的卧室"

# 指定输出文件夹和种子
python src/langchain_agent.py "生成一个现代风格的客厅" \
    --output-folder outputs/my_scene \
    --seed 42
```

### 方式 2: 使用包装脚本

```bash
cd /home/ubuntu/infinigen/infinigen_agent
python run_langchain_agent.py "生成一个北欧风格的卧室"
```

## 功能特点

### ✅ 完整流程

1. **输入验证** - 使用 GLM4.6 验证用户输入是否合理
2. **并行生成** - 同时生成颜色方案和场景
3. **智能识别** - 自动识别房间类型（Bedroom、Kitchen、LivingRoom 等）
4. **程序化生成** - 自动生成缺失的家具并应用颜色
5. **渲染输出** - 渲染单张图片（只保存最终图像）

### ✅ 官方配置

- 使用官方 hello_room 推荐配置
- `fast_solve.gin` + `singleroom.gin`
- 自动禁用地形（`terrain_enabled=False`）
- 根据用户输入自动设置房间类型限制

## 命令行参数

```bash
python src/langchain_agent.py [用户输入] [选项]

选项:
  --output-folder PATH    输出文件夹路径（默认: outputs/langchain_<timestamp>）
  --seed SEED            随机种子（默认: 随机生成）
  --timeout SECONDS      场景生成超时时间（秒，默认: 600）
  -h, --help             显示帮助信息
```

## 使用示例

### 示例 1: 交互式模式

```bash
python src/langchain_agent.py
```

然后按提示输入：
```
请输入场景描述: 生成一个北欧风格的卧室，床是白色的，沙发是浅灰色的
```

### 示例 2: 命令行模式

```bash
python src/langchain_agent.py "生成一个现代风格的客厅，沙发是蓝色的"
```

### 示例 3: 指定参数

```bash
python src/langchain_agent.py "生成一个北欧风格的卧室" \
    --output-folder outputs/nordic_bedroom \
    --seed 42 \
    --timeout 900
```

## 输出结果

执行成功后，会在输出文件夹中生成：

```
outputs/langchain_<timestamp>/
├── scene.blend              # 生成的场景文件（已应用颜色）
├── rendered_image.png       # 渲染的图片（只保存最终图像）
└── assets/                  # 场景资源
```

## 支持的房间类型

系统会自动识别以下房间类型：

- **Kitchen** - 厨房
- **Bedroom** - 卧室
- **LivingRoom** - 客厅
- **Bathroom** - 浴室
- **DiningRoom** - 餐厅
- **Closet** - 衣橱
- **Hallway** - 走廊
- **Garage** - 车库
- **Balcony** - 阳台
- **Office** - 办公室
- 等等...

## 预计时间

- **场景生成**: 8-13 分钟（使用 fast_solve 配置）
- **颜色应用**: 1-2 分钟
- **渲染图片**: 1-3 分钟
- **总计**: 约 10-18 分钟

## 注意事项

1. **首次运行**: 需要确保 Infinigen 环境已正确配置
2. **API 配置**: 需要配置 GLM4.6 和 Qwen API（在 `config/api_config.py` 中）
3. **输出目录**: 确保有足够的磁盘空间（每个场景约 50-100 MB）
4. **超时设置**: 如果场景生成时间较长，可以增加 `--timeout` 参数

## 故障排除

### 问题 1: Agent 初始化失败

**解决方案**: 检查 Infinigen 根目录是否正确，确保在正确的 conda 环境中运行

### 问题 2: 场景生成失败

**解决方案**: 
- 检查输出目录权限
- 检查 gin 配置文件是否存在
- 查看详细错误信息

### 问题 3: 颜色应用失败

**解决方案**: 
- 检查场景中是否存在对应的家具
- 检查颜色解析是否正确
- 查看程序化生成器是否支持该家具类型

## 更多信息

- 架构说明: `ARCHITECTURE.md`
- 测试指南: `TEST_GUIDE.md`

