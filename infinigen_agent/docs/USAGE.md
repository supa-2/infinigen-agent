# 使用指南

## 系统已搭建完成！

智能体系统已经完整搭建，包含以下模块：

### ✅ 已完成的功能

1. **vLLM 客户端** (`src/vllm_client.py`)
   - 连接到 Qwen2.5-7B-infinigen 模型
   - 支持聊天补全 API
   - 自动重试机制

2. **颜色解析器** (`src/color_parser.py`)
   - 从大模型输出中提取家具颜色信息
   - 支持多种格式（JSON、自然语言、正则表达式）
   - 颜色名称到 RGB 的映射

3. **场景颜色应用器** (`src/scene_color_applier.py`)
   - 在 Blender 场景中查找家具对象
   - 将颜色应用到对象的材质上
   - 保存修改后的场景

4. **主智能体** (`src/agent.py`)
   - 整合所有功能
   - 完整的处理流程

### 📝 使用方法

#### 方法1: 使用命令行脚本

```bash
cd /home/ubuntu/infinigen/infinigen_agent
conda activate infinigen

# 运行智能体
python run_agent.py "生成一个北欧风的卧室" ../outputs/hello_room/coarse/scene.blend
```

#### 方法2: 在 Python 代码中使用

```python
from src.agent import InfinigenAgent

agent = InfinigenAgent()
output_path = agent.process_request(
    user_request="生成一个北欧风的卧室",
    scene_path="../outputs/hello_room/coarse/scene.blend"
)
```

#### 方法3: 分步使用

```python
from src.vllm_client import VLLMClient
from src.color_parser import ColorParser

# 1. 获取色彩方案
client = VLLMClient()
color_scheme = client.simple_chat("生成一个北欧风的卧室")

# 2. 解析颜色
parser = ColorParser()
colors = parser.parse_colors_from_text(color_scheme)

# 3. 应用到场景（需要在 Blender 环境中）
from src.scene_color_applier import SceneColorApplier
applier = SceneColorApplier("scene.blend")
applier.apply_colors_to_scene(colors)
applier.save_scene("scene_colored.blend")
```

### ⚠️ 注意事项

1. **API 连接**: 如果遇到 500 错误，请检查：
   - API 端点是否正确
   - 模型名称是否为 "Qwen2.5-7B-infinigen"
   - API 密钥是否有效

2. **Blender 环境**: 场景颜色应用需要在 Blender 环境中运行：
   ```bash
   # 使用 Infinigen 的 Blender 环境
   python -m infinigen.launch_blender -m infinigen_agent.src.agent
   ```

3. **场景文件**: 确保输入的 .blend 文件存在且可访问

### 🔧 故障排除

如果遇到问题：

1. **测试 vLLM 连接**:
   ```bash
   python test_vllm.py
   ```

2. **检查配置**:
   编辑 `config/api_config.py` 确认 API 设置正确

3. **查看日志**: 
   运行时会输出详细的处理日志

### 📚 下一步

系统已经搭建完成，可以开始测试和使用。如果需要调整：
- 修改颜色映射：编辑 `src/color_parser.py` 中的 `COLOR_MAP`
- 修改家具关键词：编辑 `src/scene_color_applier.py` 中的 `keyword_map`
- 调整提示词：编辑 `src/agent.py` 中的 `system_prompt`

