# Agent 双模式功能说明

## 功能概述

Agent 现在支持两种工作模式：

1. **模板模式（Template Mode）**：从模板池挑选模板 → 改色 → 渲染（快速，2-3分钟）
2. **生成模式（Generate Mode）**：快速生成新场景 → 预览 → 用户确认 → 精修渲染（可选）

## 模式一：模板模式（默认）

### 特点

- ✅ 最快速度（2-3分钟）
- ✅ 使用预生成的场景模板
- ✅ 自动应用颜色方案
- ✅ 高质量 Cycles 渲染

### 使用示例

```python
from src.langchain_agent import LangChainInfinigenAgent

agent = LangChainInfinigenAgent()

# 使用模板模式（默认）
result = agent.process_request(
    user_input="生成一个红色调的北欧卧室",
    output_folder="outputs/my_bedroom",
    mode="template"  # 默认值，可省略
)

if result["success"]:
    print(f"场景文件: {result['scene_file']}")
    print(f"渲染图片: {result['rendered_image']}")
    print(f"使用模板: {result['used_template']}")
```

### 工作流程

1. 验证用户输入
2. 生成颜色方案
3. 从模板池检索并复制模板（或生成新场景）
4. 应用颜色到场景
5. Cycles 高质量渲染
6. 返回结果

## 模式二：快速生成模式

### 特点

- ✅ 生成全新场景（不依赖模板池）
- ✅ 使用更激进的快速配置（3-8分钟生成）
- ✅ 快速预览（Workbench/Eevee，<1秒）
- ✅ 用户确认后可选精修渲染

### 使用示例

#### 方式1：只生成预览，等待用户确认

```python
from src.langchain_agent import LangChainInfinigenAgent

agent = LangChainInfinigenAgent()

# 快速生成模式，只生成预览
result = agent.process_request(
    user_input="生成一个现代简约风格的客厅",
    output_folder="outputs/my_living_room",
    mode="generate",
    auto_confirm=False  # 只生成预览，不自动精修
)

if result["success"]:
    print(f"场景文件: {result['scene_file']}")
    print(f"预览图片: {result['preview_image']}")
    print(f"需要确认: {result['needs_confirmation']}")
    print(f"提示信息: {result['message']}")
    
    # 用户确认后，进行精修渲染
    if input("是否需要精修渲染？(y/n): ").lower() == 'y':
        final_result = agent.confirm_and_render(
            scene_file=result['scene_file'],
            output_folder="outputs/my_living_room"
        )
        if final_result["success"]:
            print(f"精修渲染完成: {final_result['rendered_image']}")
```

#### 方式2：自动确认，直接精修渲染

```python
# 快速生成模式，自动确认并精修渲染
result = agent.process_request(
    user_input="生成一个现代简约风格的客厅",
    output_folder="outputs/my_living_room",
    mode="generate",
    auto_confirm=True  # 自动确认，直接精修渲染
)

if result["success"]:
    print(f"场景文件: {result['scene_file']}")
    print(f"预览图片: {result['preview_image']}")
    print(f"精修渲染: {result.get('rendered_image')}")
```

### 快速生成配置

生成模式使用更激进的配置，大幅减少计算量：

```python
gin_configs = ['ultra_fast_solve.gin', 'singleroom.gin']
gin_overrides = [
    'compose_indoors.terrain_enabled=False',
    'populate.density_multiplier=0.5',  # 减少一半的装饰物
    'compose_indoors.solve_steps_large=5',  # 减少大物体布局尝试次数
]
```

### 快速预览渲染

- **引擎**: Eevee（默认）或 Workbench
- **分辨率**: 1920x1080
- **耗时**: <1秒
- **质量**: 预览级别（足以查看布局）

### 工作流程

1. 验证用户输入
2. 检测房间类型
3. 快速生成新场景（使用激进配置）
4. 快速预览渲染（Eevee，<1秒）
5. 返回预览，等待用户确认
6. （可选）用户确认后进行精修渲染（Cycles）

## 命令行使用

### 模板模式

```bash
cd /home/ubuntu/infinigen/infinigen_agent
python src/langchain_agent.py "生成一个北欧风格的卧室" \
    --output-folder outputs/my_bedroom
```

### 生成模式

```bash
# 只生成预览
python src/langchain_agent.py "生成一个现代客厅" \
    --output-folder outputs/my_living_room \
    --mode generate

# 自动确认并精修渲染
python src/langchain_agent.py "生成一个现代客厅" \
    --output-folder outputs/my_living_room \
    --mode generate \
    --auto-confirm
```

## 性能对比

| 模式 | 场景生成 | 预览 | 精修渲染 | 总耗时 |
|------|---------|------|---------|--------|
| **模板模式** | <1秒（模板） | - | ~1分钟 | **2-3分钟** |
| **生成模式（预览）** | 3-8分钟 | <1秒 | - | **3-8分钟** |
| **生成模式（完整）** | 3-8分钟 | <1秒 | ~1分钟 | **4-9分钟** |

## 选择建议

### 使用模板模式，如果：
- ✅ 需要快速结果（2-3分钟）
- ✅ 可以接受预定义的场景布局
- ✅ 主要关注颜色和材质变化

### 使用生成模式，如果：
- ✅ 需要全新的、独特的场景布局
- ✅ 不满足于模板池中的场景
- ✅ 有足够时间等待生成（3-8分钟）
- ✅ 希望先预览布局，再决定是否精修

## API 参考

### `process_request()`

```python
def process_request(
    self,
    user_input: str,
    output_folder: str,
    seed: Optional[str] = None,
    timeout: Optional[int] = None,
    mode: str = "template",  # "template" 或 "generate"
    auto_confirm: bool = False  # 仅用于 generate 模式
) -> Dict[str, Any]:
```

**参数说明**：
- `mode`: 处理模式
  - `"template"`：模板模式（默认）
  - `"generate"`：快速生成模式
- `auto_confirm`: 仅用于生成模式
  - `False`：只生成预览，等待用户确认
  - `True`：自动确认，直接进行精修渲染

### `confirm_and_render()`

```python
def confirm_and_render(
    self,
    scene_file: str,
    output_folder: Optional[str] = None
) -> Dict[str, Any]:
```

**用途**：在生成模式下，用户确认后进行精修渲染。

## 完整示例

```python
from src.langchain_agent import LangChainInfinigenAgent

agent = LangChainInfinigenAgent()

# 示例1: 模板模式（最快）
print("=" * 60)
print("示例1: 模板模式")
print("=" * 60)
result1 = agent.process_request(
    user_input="生成一个红色调的北欧卧室",
    output_folder="outputs/bedroom_template",
    mode="template"
)
print(f"模板模式结果: {result1['success']}")

# 示例2: 生成模式（预览）
print("\n" + "=" * 60)
print("示例2: 生成模式（预览）")
print("=" * 60)
result2 = agent.process_request(
    user_input="生成一个现代简约风格的客厅",
    output_folder="outputs/living_room_generate",
    mode="generate",
    auto_confirm=False
)

if result2["success"] and result2.get("needs_confirmation"):
    print(f"预览图片: {result2['preview_image']}")
    
    # 用户确认
    user_choice = input("是否进行精修渲染？(y/n): ")
    if user_choice.lower() == 'y':
        final_result = agent.confirm_and_render(
            scene_file=result2['scene_file']
        )
        print(f"精修渲染: {final_result.get('rendered_image')}")
```

## 注意事项

1. **模板池要求**：模板模式需要预先生成模板池
   ```bash
   python tools/generate_template_pool.py --all
   ```

2. **生成时间**：生成模式的场景生成可能需要 3-8 分钟，请耐心等待

3. **预览质量**：快速预览使用 Eevee 引擎，质量较低但速度很快，主要用于查看布局

4. **精修渲染**：精修渲染使用 Cycles 引擎，质量高但耗时较长（约1分钟）

