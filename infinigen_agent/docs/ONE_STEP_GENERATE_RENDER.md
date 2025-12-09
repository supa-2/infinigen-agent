# 一步完成生成和渲染

## Infinigen 原生支持

### ✅ 是的，可以一步完成！

Infinigen 的 `generate_indoors` 命令支持一次执行多个任务：

```bash
# 一步完成生成和渲染
python -m infinigen_examples.generate_indoors \
    --output_folder outputs/test \
    -s 12345 \
    -g base disable/no_objects \
    -t coarse render
```

**关键点：**
- `-t` 参数支持 `nargs="+"`，可以接受多个任务
- 可以同时指定 `coarse` 和 `render`
- 会按顺序执行：先 `coarse`（生成场景），再 `render`（渲染）

## Agent 的实现

### 方式 1: 一步完成（推荐，默认）

```python
from src.scene_generator import SceneGenerator

generator = SceneGenerator()

# 一步完成生成和渲染
result = generator.generate_and_render(
    output_folder="outputs/test",
    seed="12345",
    one_step=True  # 默认 True
)

print(f"场景文件: {result['scene_file']}")
print(f"渲染输出: {result['render_output']}")
```

**内部实现：**
```python
# 使用 -t coarse render 一次完成
generator.generate_scene(
    output_folder="outputs/test",
    seed="12345",
    task=["coarse", "render"]  # 多个任务
)
```

### 方式 2: 直接指定多个任务

```python
# 直接使用 generate_scene，指定多个任务
scene_file = generator.generate_scene(
    output_folder="outputs/test",
    seed="12345",
    task=["coarse", "render"]  # 或 "coarse render"
)
```

### 方式 3: 分步执行（兼容旧方式）

```python
# 如果需要分步执行
result = generator.generate_and_render(
    output_folder="outputs/test",
    seed="12345",
    one_step=False  # 分两步执行
)
```

## 对比

| 方式 | 命令 | 优点 | 缺点 |
|------|------|------|------|
| **一步完成** | `-t coarse render` | ✅ 更快<br>✅ 更简单<br>✅ 和原生一致 | - |
| **分步执行** | 先 `-t coarse`<br>再 `-t render` | ✅ 可以单独控制 | ⚠️ 需要两次调用<br>⚠️ 更慢 |

## 使用示例

### 示例 1: 一步完成（推荐）

```python
generator = SceneGenerator()

# 一步完成生成和渲染
result = generator.generate_and_render(
    output_folder="outputs/my_scene",
    seed="a1b2c3d4",
    gin_configs=['base', 'disable/no_objects'],
    timeout=600  # 10分钟超时
)

# 结果包含场景文件和渲染输出
scene_file = result['scene_file']  # outputs/my_scene/coarse/scene.blend
render_output = result['render_output']  # outputs/my_scene/coarse/frames
```

### 示例 2: 只生成场景

```python
# 只生成场景，不渲染
scene_file = generator.generate_scene(
    output_folder="outputs/my_scene",
    seed="a1b2c3d4",
    task="coarse"  # 单个任务
)
```

### 示例 3: 只渲染已有场景

```python
# 渲染已有场景
render_output = generator.generate_scene(
    output_folder="outputs/my_scene/frames",
    seed="a1b2c3d4",
    task="render"  # 单个任务
)
```

## 技术细节

### 命令构建

```python
# 单个任务
cmd = ['python', '-m', 'infinigen_examples.generate_indoors', 
       '--output_folder', '...', '-s', '...', '-t', 'coarse']

# 多个任务（一步完成）
cmd = ['python', '-m', 'infinigen_examples.generate_indoors', 
       '--output_folder', '...', '-s', '...', '-t', 'coarse', 'render']
```

### 执行顺序

Infinigen 会按顺序执行任务：
1. `coarse` - 生成场景
2. `render` - 渲染场景

如果 `coarse` 失败，`render` 不会执行。

## 优势

### ✅ 使用一步完成的优势

1. **更快**：不需要两次启动 Blender
2. **更简单**：一个命令完成所有操作
3. **更一致**：和 Infinigen 原生脚本一致
4. **更可靠**：原子操作，要么全部成功，要么全部失败

## 总结

✅ **推荐使用一步完成方式**（`one_step=True`，默认）

这样可以：
- 利用 Infinigen 原生命令的优势
- 更快、更简单
- 和原生脚本行为一致
