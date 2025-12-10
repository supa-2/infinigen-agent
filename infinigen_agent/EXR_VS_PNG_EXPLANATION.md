# EXR vs PNG 输出格式说明

## 问题：为什么官方文档说能直接生成图片，但我这边只生成了 EXR？

## 答案

### 1. Infinigen 的渲染机制

Infinigen 的 `render_image` 函数使用 Blender 的 Compositor（合成器）来输出图片。根据代码分析：

**在 `configure_compositor_output` 函数中（`infinigen/core/rendering/render.py`）：**

```python
# 创建两个输出节点：PNG 和 EXR
file_output_node_png = nw.new_node(Nodes.OutputFile, attrs={
    "format.file_format": "PNG",
    ...
})
file_output_node_exr = nw.new_node(Nodes.OutputFile, attrs={
    "format.file_format": "OPEN_EXR",
    ...
})

# 默认输出节点：如果不是 ground truth，使用 PNG
default_file_output_node = (
    file_output_node_exr if saving_ground_truth else file_output_node_png
)

# 关键代码：即使 saving_ground_truth=False，也会同时链接到 EXR
if saving_ground_truth:
    slot_input.path = "UniqueInstances"
else:
    nw.links.new(image, file_output_node_exr.inputs["Image"])  # 链接到 EXR
    file_slot_list.append(file_output_node_exr.file_slots[slot_input.path])
file_slot_list.append(default_file_output_node.file_slots[slot_input.path])  # 链接到 PNG
```

### 2. 为什么只看到 EXR 文件？

虽然代码理论上会同时生成 PNG 和 EXR，但在实际运行中：

1. **Blender Compositor 的行为**：在某些情况下，Blender 的 Compositor 可能只成功输出了 EXR 格式
2. **文件命名问题**：PNG 文件可能被生成但命名不同，或者保存到了不同的位置
3. **配置差异**：不同的 gin 配置可能导致不同的输出行为

### 3. 官方命令的输出

根据 `docs/HelloRoom.md`，官方命令是：

```bash
# 生成场景
python -m infinigen_examples.generate_indoors --seed 0 --task coarse --output_folder outputs/indoors/coarse ...

# 渲染图片（单独步骤）
python -m infinigen_examples.generate_indoors --seed 0 --task render --input_folder outputs/indoors/coarse --output_folder outputs/indoors/frames
```

官方命令在渲染阶段（`--task render`）可能会：
- 使用特定的 gin 配置来确保输出 PNG
- 或者官方文档中的"图片"指的是 EXR 文件（EXR 也是图片格式，只是需要特殊软件查看）

### 4. 解决方案

#### 方案 1：使用我们的转换脚本（推荐）

我们已经提供了 EXR 转 PNG 的转换逻辑，集成在 `scene_renderer.py` 中：

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("scene.blend")
renderer.render_image("output.png")  # 自动转换 EXR 到 PNG
```

#### 方案 2：手动转换

使用我们提供的测试脚本：

```bash
cd /home/ubuntu/infinigen
python3 infinigen_agent/test_exr_simple.py
```

#### 方案 3：检查是否有 PNG 文件

PNG 文件可能被生成但命名不同，检查一下：

```bash
find outputs/test_langchain_1765279816/frames -name "*.png"
```

### 5. 为什么需要 EXR 转 PNG？

1. **EXR 格式特点**：
   - 高动态范围（HDR）格式
   - 32 位浮点数，支持超过 1.0 的亮度值
   - 文件较大
   - 需要特殊软件查看（如 Blender、专业图像软件）

2. **PNG 格式特点**：
   - 标准图片格式
   - 8 位整数（0-255）
   - 文件较小
   - 任何图片查看器都能打开

3. **转换过程**：
   - 读取 EXR（浮点数，可能 > 1.0）
   - 应用 tone mapping（如果值 > 1.0）
   - 缩放到 0-255 范围
   - 转换为 uint8
   - 保存为 PNG

### 6. 总结

- **官方命令理论上会生成 PNG**，但在某些情况下可能只生成 EXR
- **EXR 也是图片格式**，只是需要转换才能用普通查看器打开
- **我们的代码已经处理了这个问题**：自动检测 EXR 并转换为 PNG
- **如果转换失败**，代码会返回 EXR 文件路径，你可以手动转换

### 7. 验证方法

检查你的输出目录：

```bash
# 查找所有图片文件
find outputs/test_langchain_1765279816/frames -type f \( -name "*.png" -o -name "*.exr" \)

# 如果只有 EXR，使用转换脚本
python3 infinigen_agent/test_exr_simple.py
```

