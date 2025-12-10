# 快速开始：获取 PNG 图片

## 一句话总结

**你只需要 PNG？没问题！代码会自动转换 EXR 为 PNG，你不需要关心格式问题。**

## 方法 1：使用渲染器（推荐）✅

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

# 激活 infinigen 环境后运行
renderer = SceneRenderer("scene.blend")
png_path = renderer.render_image("output.png")  # 总是返回 PNG！
```

## 方法 2：转换现有 EXR 文件

```bash
# 激活 infinigen 环境
conda activate infinigen

# 转换 EXR 到 PNG
python infinigen_agent/convert_exr_to_png.py path/to/image.exr -o output.png
```

## 环境要求

**必须在 infinigen conda 环境中运行！**

```bash
conda activate infinigen
pip install OpenEXR imageio  # 如果还没有安装
```

## 示例

```bash
# 转换你的测试文件
conda activate infinigen
python infinigen_agent/convert_exr_to_png.py \
  outputs/test_langchain_1765279816/frames/Image/camera_0/Image_0_0_0001_0.exr \
  -o outputs/test_langchain_1765279816/rendered_image.png
```

## 技术细节

- ✅ 使用 OpenEXR 库读取 EXR（更可靠）
- ✅ 使用 Reinhard tone mapping 处理 HDR
- ✅ 自动处理多通道和灰度图
- ✅ 总是输出标准 PNG 格式

**就这么简单！** 🎉

