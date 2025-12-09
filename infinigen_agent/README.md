# Infinigen Agent - 智能场景生成系统

基于 Infinigen 和大语言模型的智能室内场景生成系统。

## 功能

- **自动生成场景**: 从用户输入自动生成 3D 场景（无需手动准备场景文件）
- **智能色彩方案**: 大模型（Qwen2.5-7B-infinigen）分析用户描述并生成家具色彩方案
- **自动应用颜色**: 自动将色彩应用到场景中的家具
- **渲染功能**: 支持渲染图片和视频

## 项目结构

```
infinigen_agent/
├── README.md                 # 项目主文档
├── requirements.txt          # Python 依赖
├── run_agent.py             # 主运行脚本
│
├── config/                   # 配置文件
│   ├── __init__.py
│   └── api_config.py        # vLLM API 配置
│
├── src/                      # 核心源代码
│   ├── __init__.py
│   ├── agent.py             # 主智能体
│   ├── vllm_client.py       # vLLM 客户端
│   ├── color_parser.py      # 颜色解析器
│   ├── scene_color_applier.py  # 场景颜色应用器
│   ├── scene_generator.py   # 场景生成器
│   └── scene_renderer.py    # 场景渲染器
│
├── docs/                      # 文档目录
│   ├── QUICK_START.md        # 快速开始指南
│   ├── AUTO_GENERATE.md      # 自动生成场景说明
│   ├── RENDERING.md          # 渲染功能说明
│   ├── TROUBLESHOOTING.md    # 故障排除指南
│   ├── TESTING.md            # 测试文档
│   └── ...                    # 其他文档
│
├── tests/                    # 测试文件
│   ├── test_vllm.py         # vLLM 测试
│   ├── test_color_parser.py  # 颜色解析测试
│   ├── test_render.py        # 渲染测试
│   ├── test_auto_generate.py # 自动生成测试
│   └── ...                    # 其他测试
│
├── scripts/                   # Shell 脚本
│   ├── quick_generate.sh     # 快速生成场景
│   ├── install_terrain_deps.sh  # 安装地形依赖
│   ├── fix_marching_cubes.sh    # 修复 marching_cubes
│   ├── run_from_anywhere.sh     # 从任意目录运行
│   └── ...                    # 其他脚本
│
└── tools/                     # 工具脚本（Python）
    ├── quick_test_vllm.py    # 快速测试 vLLM
    ├── generate_scene_direct.py  # 直接生成场景
    ├── monitor_render.py     # 监控渲染
    └── ...                    # 其他工具
```

## 快速开始

### 1. 安装依赖

```bash
conda activate infinigen
pip install -r requirements.txt
```

### 2. 测试 vLLM 连接

```bash
python test_vllm.py
```

### 3. 使用智能体生成场景

```bash
# 方式1: 自动生成场景（推荐，从零开始）
python run_agent.py "生成一个北欧风的卧室" \
    --auto-generate \
    --output-folder outputs/my_room \
    --render-image

# 方式2: 使用已有场景文件
python run_agent.py "生成一个北欧风的卧室" ../outputs/hello_room/coarse/scene.blend

# 指定输出文件
python run_agent.py "生成一个现代简约风格的客厅" input.blend -o output_colored.blend
```

### 4. 在代码中使用

```python
from src.agent import InfinigenAgent

agent = InfinigenAgent()
output_path = agent.process_request(
    user_request="生成一个北欧风的卧室",
    scene_path="scene.blend"
)
```

## 工作流程

1. **用户输入** → 自然语言描述（如"北欧风卧室"）
2. **大模型分析** → 调用 Qwen2.5-7B-infinigen 生成色彩方案
3. **颜色解析** → 从模型输出中提取家具和颜色信息
4. **场景修改** → 将颜色应用到 Blender 场景中的对应家具
5. **保存输出** → 生成带颜色的场景文件

## 配置

编辑 `config/api_config.py` 修改：
- API 端点
- API 密钥
- 模型名称（当前：Qwen2.5-7B-infinigen）

## 支持的家具类型

- 床、床头柜
- 沙发、茶几、电视柜
- 餐桌、餐椅
- 书桌、书柜、书架
- 衣柜、储物柜
- 窗帘、地毯、地板
- 墙壁、灯具等

## 支持的颜色

- 基础色：白色、黑色、灰色等
- 暖色调：米白色、原木色、棕色等
- 北欧风格：北欧白、浅木色、浅灰色等
- 其他常见颜色

## 测试脚本

### 综合测试
运行所有测试：
```bash
./test_all.sh
```

### 渲染测试
```bash
# 运行渲染测试
./run_render_test.sh

# 检查渲染状态
./check_render_status.sh
```

### Python 测试
```bash
# vLLM 连接测试
python test_vllm.py

# 颜色解析测试
python test_color_parser.py

# 简单渲染测试
python test_render_simple.py

# 快速渲染测试
python quick_render_test.py
```

## 渲染功能

详细说明请参考 [RENDERING.md](RENDERING.md)

### 快速示例
```bash
# 生成场景并渲染图片
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --render-image \
    --resolution 1920 1080

# 生成场景并渲染视频
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --render-video \
    --video-frames 60 \
    --video-fps 24
```

## 注意事项

- 需要在 Blender 环境中运行（使用 bpy 模块）
- 场景文件必须是 .blend 格式
- 确保 vLLM API 服务可访问
- 渲染功能需要 Infinigen 渲染模块支持
- 视频功能需要安装 ffmpeg: `sudo apt install ffmpeg`
