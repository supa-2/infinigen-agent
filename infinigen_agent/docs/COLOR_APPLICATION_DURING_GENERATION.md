# 生成场景时同步应用颜色

## 问题

Infinigen 原生命令不支持修改家具颜色，但 Agent 需要在生成场景时同步应用颜色。

## 解决方案

### ✅ 回调机制（已实现）

在场景生成完成后，立即通过回调函数应用颜色：

```python
# 在 generate_scene 中添加回调参数
scene_file = generator.generate_scene(
    output_folder="outputs/test",
    seed="12345",
    task="coarse",
    apply_colors_callback=apply_colors_function  # 回调函数
)
```

### 工作流程

1. **调用原生命令生成场景**
   ```bash
   python -m infinigen_examples.generate_indoors \
       --output_folder outputs/test \
       -s 12345 \
       -t coarse
   ```

2. **场景生成完成后，立即应用颜色**
   - 加载生成的场景文件
   - 解析用户请求中的颜色信息
   - 应用颜色到家具
   - 保存带颜色的场景文件

3. **返回带颜色的场景文件**

## 使用方式

### 方式 1: 自动检测（推荐）

Agent 会自动检测用户请求中是否包含颜色需求：

```python
agent = InfinigenAgent()

# 自动检测颜色需求并应用
scene_file = agent.generate_scene_from_request(
    user_request="生成一个北欧风的卧室，床是白色的，沙发是蓝色的",
    output_folder="outputs/test",
    seed="12345"
)
# 会自动在生成后应用颜色
```

### 方式 2: 手动指定回调

```python
generator = SceneGenerator()

def apply_colors(scene_path: Path) -> str:
    """应用颜色的回调函数"""
    from src.scene_color_applier import SceneColorApplier
    applier = SceneColorApplier(str(scene_path))
    # ... 应用颜色逻辑
    return colored_scene_path

scene_file = generator.generate_scene(
    output_folder="outputs/test",
    seed="12345",
    apply_colors_callback=apply_colors
)
```

## 颜色检测逻辑

Agent 会自动检测以下关键词：

- **中文**：颜色、色彩、色、红色、蓝色、绿色、黄色、白色、黑色
- **英文**：color, colour, red, blue, green, yellow, white, black
- **风格**：北欧、现代、风格、style

如果检测到这些关键词，会自动应用颜色。

## 优势

### ✅ 与原生流程无缝集成

- 使用 Infinigen 原生命令生成场景
- 生成完成后立即应用颜色
- 不需要修改 Infinigen 源码

### ✅ 灵活性

- 可以选择是否应用颜色
- 可以自定义颜色应用逻辑
- 不影响原生命令的执行

### ✅ 可靠性

- 如果颜色应用失败，仍返回原始场景
- 不会影响场景生成流程
- 错误处理完善

## 技术实现

### 回调函数签名

```python
def apply_colors_callback(scene_path: Path) -> str:
    """
    应用颜色的回调函数
    
    Args:
        scene_path: 生成的场景文件路径
        
    Returns:
        应用颜色后的场景文件路径
    """
    # 加载场景
    # 应用颜色
    # 保存场景
    return colored_scene_path
```

### 执行时机

回调函数在以下时机执行：
1. ✅ 场景生成成功
2. ✅ 找到场景文件
3. ✅ 在返回场景文件之前

### 错误处理

如果回调函数执行失败：
- ⚠️ 记录错误日志
- ⚠️ 返回原始场景文件
- ✅ 不影响主流程

## 示例

### 完整流程示例

```python
from src.agent import InfinigenAgent

agent = InfinigenAgent()

# 一步完成：生成场景 + 应用颜色 + 渲染图片
results = agent.process_request_with_auto_generate(
    user_request="生成一个北欧风的卧室，床是白色的，沙发是蓝色的",
    output_folder="outputs/my_scene",
    seed="a1b2c3d4",
    render_image=True
)

print(f"场景文件: {results['colored_scene']}")
print(f"渲染图片: {results['image']}")
```

### 执行流程

```
1. 调用 Infinigen 原生命令生成场景
   ↓
2. 场景生成成功，找到 scene.blend
   ↓
3. 检测到颜色需求，调用回调函数
   ↓
4. 加载场景，应用颜色，保存 colored_scene.blend
   ↓
5. 返回带颜色的场景文件
   ↓
6. 渲染图片（可选）
```

## 总结

✅ **已实现**：在生成场景时同步应用颜色

✅ **优势**：
- 与原生流程无缝集成
- 自动检测颜色需求
- 错误处理完善

✅ **使用**：直接调用 `generate_scene_from_request`，Agent 会自动处理颜色应用
