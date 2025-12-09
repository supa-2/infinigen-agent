# LangChain Infinigen Agent 使用文档

## 概述

基于 LangChain 的完备 Agent 系统，实现：
1. **GLM4.6** 验证用户输入
2. **Qwen2.5-7b-infinigen** 生成家具颜色方案
3. **Infinigen 原生命令** 生成场景
4. 应用颜色到场景（替换原文件）
5. 渲染图片返回给用户

## 架构

```
用户输入
  ↓
GLM4.6 验证输入
  ↓ (合理)
并行执行:
  ├─ Qwen2.5-7b-infinigen 生成颜色方案
  └─ Infinigen 原生命令生成场景
  ↓
应用颜色到场景（替换原文件）
  ↓
渲染图片
  ↓
返回结果
```

## 安装依赖

```bash
cd /home/ubuntu/infinigen/infinigen_agent
pip install -r requirements.txt
```

## 使用方法

### 方式 1: 命令行模式

```bash
python run_langchain_agent.py "生成一个北欧风的卧室，床是白色的，沙发是蓝色的"
```

### 方式 2: 交互式模式

```bash
python run_langchain_agent.py
```

然后输入场景描述，输入 `quit` 退出。

### 方式 3: Python API

```python
from src.langchain_agent import LangChainInfinigenAgent

# 初始化 Agent
agent = LangChainInfinigenAgent(
    infinigen_root="/home/ubuntu/infinigen",
    glm_api_key="sk-QEBvsYNQh6pvLotdR4DK1w",
    glm_base_url="https://llmapi.paratera.com"
)

# 处理请求
result = agent.process_request(
    user_input="生成一个北欧风的卧室，床是白色的，沙发是蓝色的",
    output_folder="/home/ubuntu/infinigen/outputs/my_scene",
    seed="a1b2c3d4",
    timeout=600  # 10分钟超时
)

if result.get("success"):
    print(f"场景文件: {result['scene_file']}")
    print(f"渲染图片: {result['rendered_image']}")
else:
    print(f"错误: {result.get('error')}")
```

## 工作流程

### 步骤 1: 输入验证

使用 GLM4.6 模型验证用户输入是否合理：

- ✅ **合理输入**：描述室内场景，包含家具和颜色要求
- ❌ **不合理输入**：无关内容、过于模糊、不合理要求

如果不合理，Agent 会返回错误和建议，要求用户重新输入。

### 步骤 2: 并行生成

**2.1 生成颜色方案**（Qwen2.5-7b-infinigen）
- 分析用户输入
- 提取场景类型、风格、家具颜色
- 生成 JSON 格式的颜色方案

**2.2 生成场景**（Infinigen 原生命令）
- 调用 `python -m infinigen_examples.generate_indoors`
- 使用 `-t coarse` 生成场景
- 保存到指定输出文件夹

### 步骤 3: 应用颜色

- 解析颜色方案 JSON
- 加载生成的场景文件
- 查找场景中的家具对象
- 应用颜色到对应家具
- **保存场景（替换原文件，不生成新文件）**

### 步骤 4: 渲染图片

- 使用场景渲染器渲染图片
- 保存到场景文件夹
- 返回图片路径

## API 配置

### GLM4.6 配置

```python
glm_llm = ChatOpenAI(
    model="glm-4",
    api_key="sk-QEBvsYNQh6pvLotdR4DK1w",
    base_url="https://llmapi.paratera.com",
    temperature=0.3
)
```

### Qwen 配置

```python
qwen_llm = ChatOpenAI(
    model="qwen2.5-7b-infinigen",
    api_key="sk-QEBvsYNQh6pvLotdR4DK1w",  # 使用相同的 API key
    base_url="https://llmapi.paratera.com",
    temperature=0.7
)
```

## 返回结果格式

### 成功

```python
{
    "success": True,
    "user_input": "用户输入",
    "scene_file": "/path/to/scene.blend",
    "rendered_image": "/path/to/rendered_image.png",
    "color_scheme": "{...JSON...}",
    "colors_applied": 3
}
```

### 失败

```python
{
    "success": False,
    "error": "错误类型",
    "message": "错误消息",
    "suggestion": "建议（如果是输入不合理）"
}
```

## 特性

### ✅ 输入验证

- 自动检测不合理输入
- 提供修改建议
- 要求重新输入

### ✅ 并行处理

- 颜色生成和场景生成并行执行
- 提高效率

### ✅ 颜色应用

- 自动解析颜色方案
- 智能匹配家具对象
- 直接替换原场景文件

### ✅ 错误处理

- 完善的错误处理机制
- 详细的错误信息
- 部分失败时返回已有结果

## 示例

### 示例 1: 成功场景

```bash
$ python run_langchain_agent.py "生成一个现代风格的客厅，沙发是蓝色的，茶几是白色的"

步骤1: 验证用户输入...
✓ 输入验证通过: 合理：这是一个清晰的室内场景描述

步骤2: 并行生成颜色方案和场景...
  2.1 生成家具颜色方案...
  ✓ 颜色方案生成成功
  2.2 生成场景（使用 Infinigen 原生命令）...
  ✓ 场景生成成功: /path/to/scene.blend

步骤3: 应用颜色到场景...
  ✓ 沙发: 已应用颜色 蓝色
  ✓ 茶几: 已应用颜色 白色
  ✓ 颜色已应用到场景并保存: /path/to/scene.blend

步骤4: 渲染场景图片...
  ✓ 图片渲染成功: /path/to/rendered_image.png

✓ 处理完成！
```

### 示例 2: 输入不合理

```bash
$ python run_langchain_agent.py "帮我写一首诗"

步骤1: 验证用户输入...
✗ 输入不合理: 不合理：这不是场景生成请求，请描述一个室内场景，如"生成一个卧室"

建议: 请重新输入一个合理的场景描述
```

## 注意事项

1. **场景文件替换**：颜色应用后会直接替换原场景文件，不生成新文件
2. **超时设置**：场景生成可能需要 5-15 分钟，建议设置合适的超时时间
3. **API 限制**：注意 API 调用频率限制
4. **Blender 环境**：需要在 Blender Python 环境中运行

## 故障排除

### 问题 1: API 调用失败

**症状**：`GLM4.6 验证失败` 或 `Qwen 颜色生成失败`

**解决**：
- 检查 API key 是否正确
- 检查网络连接
- 检查 API 服务是否可用

### 问题 2: 颜色解析失败

**症状**：`无法解析颜色方案`

**解决**：
- 检查模型输出格式
- 查看 `color_scheme` 字段的内容
- 可能需要调整 Qwen 的 prompt

### 问题 3: 场景生成失败

**症状**：`场景生成失败`

**解决**：
- 检查 Infinigen 环境
- 检查输出文件夹权限
- 查看详细错误信息

## 总结

LangChain Infinigen Agent 提供了一个完整的端到端解决方案：
- ✅ 输入验证
- ✅ 智能颜色生成
- ✅ 场景生成
- ✅ 颜色应用
- ✅ 图片渲染

所有步骤无缝集成，用户只需提供场景描述即可获得带颜色的渲染图片。

