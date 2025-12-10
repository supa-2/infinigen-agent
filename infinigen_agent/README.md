# Infinigen Agent

基于 LangChain 的 Infinigen 场景生成 Agent，支持根据自然语言描述自动生成、修改和渲染 3D 场景。

## 🚀 快速开始

### 方式 1: 直接运行主脚本（推荐）

```bash
cd /home/ubuntu/infinigen/infinigen_agent

# 交互式模式
python src/langchain_agent.py

# 命令行模式
python src/langchain_agent.py "生成一个北欧风格的卧室"

# 使用官方推荐的 seed 0（最快）
python src/langchain_agent.py "生成一个餐厅" --seed 0
```

### 方式 2: 从已有场景继续处理

```bash
# 只渲染图片（不应用颜色）
python continue_from_scene.py outputs/xxx/scene.blend

# 应用颜色并渲染
python continue_from_scene.py outputs/xxx/scene.blend "生成一个北欧风格的卧室"
```

## ✨ 主要功能

1. **输入验证** - 使用 GLM4.6 验证用户输入是否合理
2. **智能识别** - 自动识别房间类型（Bedroom、Kitchen、LivingRoom 等）
3. **并行生成** - 同时生成颜色方案和场景
4. **程序化生成** - 自动生成缺失的家具并应用颜色
5. **自动渲染** - 场景生成完成后自动渲染图片

## 📁 项目结构

```
infinigen_agent/
├── src/                          # 核心源代码
│   ├── langchain_agent.py        # 主入口（推荐使用）
│   ├── scene_generator.py        # 场景生成器
│   ├── scene_renderer.py         # 场景渲染器
│   ├── scene_color_applier.py    # 颜色应用器
│   └── ...
├── tests/                        # 测试文件
├── tools/                        # 工具脚本
├── docs/                         # 文档
├── config/                       # 配置文件
└── scripts/                      # Shell 脚本
```

详细结构说明请查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📖 文档

- [USAGE.md](USAGE.md) - 详细使用指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构说明
- [TEST_GUIDE.md](TEST_GUIDE.md) - 测试指南
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构说明

## ⚙️ 配置

### 性能优化

- 默认使用 `ultra_fast_solve.gin` 配置（预计 5-10 分钟）
- 随机 seed 范围：0-10000（较小的 seed 通常生成更快的场景）
- 自动检测房间类型并优化配置

### API 配置

编辑 `config/api_config.py` 配置：
- GLM4.6 API（用于输入验证）
- Qwen2.5-7B API（用于颜色生成）

## 🔧 依赖

- Python 3.11+
- Blender（已集成）
- Infinigen
- LangChain
- vLLM API 访问

## 📝 使用示例

### 完整流程

```bash
python src/langchain_agent.py "生成一个现代风格的客厅" --seed 0
```

这会自动执行：
1. 验证输入
2. 生成颜色方案
3. 生成场景（5-10 分钟）
4. 应用颜色
5. 渲染图片

### 只渲染已有场景

```bash
python continue_from_scene.py outputs/xxx/scene.blend
```

## 🐛 问题排查

如果遇到问题，请查看：
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - 常见问题解决方案
- 检查日志输出中的错误信息

## 📄 许可证

本项目基于 Infinigen 项目开发。

