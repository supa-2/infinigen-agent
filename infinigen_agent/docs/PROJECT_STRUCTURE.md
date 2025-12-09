# 项目结构说明

## 推荐的项目结构

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
│   └── scene_renderer.py    # 场景渲染器
│
├── tests/                    # 测试文件（建议）
│   ├── test_vllm.py         # vLLM 测试
│   ├── test_vllm_simple.py
│   ├── test_color_parser.py
│   ├── test_render.py
│   ├── test_render_simple.py
│   ├── quick_test_vllm.py
│   └── test_all.sh          # 综合测试脚本
│
├── scripts/                  # 工具脚本（建议）
│   ├── check_render_status.sh
│   ├── run_render_test.sh
│   ├── create_video.py
│   ├── create_static_video.sh
│   ├── create_video_from_scene.sh
│   ├── render_video.py
│   ├── monitor_render.py
│   └── start_render.sh
│
└── docs/                     # 文档（建议）
    ├── QUICK_START.md       # 快速开始
    ├── RENDERING.md         # 渲染功能说明
    ├── USAGE.md             # 使用说明
    ├── COLOR_LOGIC.md       # 颜色逻辑
    ├── FURNITURE_LOCATIONS.md
    ├── CHANGELOG.md
    └── video_time_estimate.md
```

## 当前文件分类

### 核心文件（保留在根目录）
- `run_agent.py` - 主运行脚本
- `README.md` - 项目文档
- `requirements.txt` - 依赖列表

### 测试文件（建议移动到 tests/）
- `test_vllm.py`
- `test_vllm_simple.py`
- `quick_test_vllm.py`
- `test_color_parser.py`
- `test_english_input.py`
- `test_render.py`
- `test_render_simple.py`
- `test_all.sh`

### 脚本文件（建议移动到 scripts/）
- `check_render_status.sh`
- `run_render_test.sh`
- `create_static_video.sh`
- `create_video_from_scene.sh`
- `create_video.py`
- `monitor_render.py`
- `quick_render_test.py`
- `render_test.py`
- `render_video_simple.sh`
- `render_video.py`
- `start_render.sh`

### 文档文件（建议移动到 docs/）
- `QUICK_START.md`
- `RENDERING.md`
- `USAGE.md`
- `COLOR_LOGIC.md`
- `FURNITURE_LOCATIONS.md`
- `CHANGELOG.md`
- `video_time_estimate.md`

## 整理命令

如果需要整理项目结构，可以运行：

```bash
cd /home/ubuntu/infinigen/infinigen_agent

# 创建目录
mkdir -p tests scripts docs

# 移动测试文件
mv test_*.py quick_test_vllm.py test_all.sh tests/

# 移动脚本文件
mv *.sh render_*.py create_*.py monitor_render.py scripts/

# 移动文档文件（保留 README.md）
mv QUICK_START.md RENDERING.md USAGE.md COLOR_LOGIC.md FURNITURE_LOCATIONS.md CHANGELOG.md video_time_estimate.md docs/
```

## 注意事项

移动文件后，需要更新：
1. 脚本中的路径引用
2. README.md 中的路径说明
3. 测试脚本中的导入路径
