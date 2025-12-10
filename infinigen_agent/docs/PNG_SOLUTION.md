# PNG 输出解决方案

## 问题
你只需要 PNG 格式的图片，但 Infinigen 默认输出 EXR 格式。

## 解决方案

### 方案 1：使用渲染器（自动转换）✅ 推荐

`scene_renderer.py` 已经集成了自动转换功能，**总是输出 PNG**：

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("scene.blend")
# 自动转换 EXR 到 PNG，总是返回 PNG 路径
png_path = renderer.render_image("output.png")
```

**特点：**
- ✅ 自动检测 EXR 并转换为 PNG
- ✅ 使用 Reinhard tone mapping 处理 HDR
- ✅ 总是返回 PNG 文件路径
- ✅ 无需手动操作

### 方案 2：转换现有的 EXR 文件

如果你已经有 EXR 文件，使用转换脚本：

```bash
# 基本用法（自动生成 PNG 文件名）
python infinigen_agent/convert_exr_to_png.py path/to/image.exr

# 指定输出路径
python infinigen_agent/convert_exr_to_png.py path/to/image.exr -o output.png

# 静默模式
python infinigen_agent/convert_exr_to_png.py path/to/image.exr -q
```

**示例：**
```bash
# 转换你的测试文件
python infinigen_agent/convert_exr_to_png.py \
  outputs/test_langchain_1765279816/frames/Image/camera_0/Image_0_0_0001_0.exr \
  -o outputs/test_langchain_1765279816/rendered_image.png
```

### 方案 3：批量转换

```bash
# 转换目录下所有 EXR 文件
find outputs/test_langchain_1765279816/frames -name "*.exr" | while read exr; do
    python infinigen_agent/convert_exr_to_png.py "$exr"
done
```

## 转换技术细节

### Tone Mapping（色调映射）

EXR 是 HDR（高动态范围）格式，值可能超过 1.0。我们使用 **Reinhard tone mapping**：

```python
# 如果值 > 1.0，使用 tone mapping
exr_image = exr_image / (1 + exr_image)  # Reinhard
exr_image = (np.clip(exr_image, 0, 1) * 255).astype(np.uint8)
```

这确保了：
- ✅ 高亮度区域不会过曝
- ✅ 细节得到保留
- ✅ 输出适合标准图片查看器

## 环境要求

**重要：需要在 infinigen conda 环境中运行！**

```bash
# 激活 infinigen 环境
conda activate infinigen

# 安装依赖（如果还没有）
pip install OpenEXR imageio
```

## 总结

**最简单的方法：**
1. ✅ 使用 `SceneRenderer.render_image()` - 自动处理一切，总是返回 PNG
2. ✅ 或者使用 `convert_exr_to_png.py` 转换现有文件

**你不需要关心 EXR，代码会自动处理！** 🎉

**记住：在 infinigen conda 环境中运行！**

