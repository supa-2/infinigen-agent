# 渲染输出说明

## 当前设置

### 默认输出

根据代码设置，当前会生成：

1. **PNG格式图片** - 1张（主要输出）
   - 格式：`Image_0_0_0001_0.png` 或类似
   - 位置：`frames_render_{timestamp}/` 目录
   - 然后复制到指定的输出路径

2. **EXR格式图片**（可选，如果配置了）
   - 格式：`Image_0_0_0001_0.exr`
   - 用于高动态范围渲染

### 代码设置

```python
# scene_renderer.py
if passes_to_save is None:
    passes_to_save = [("Image", "Image")]  # 只渲染Image通道
```

**当前设置**: 只渲染 **1个通道（Image）**，所以应该只生成 **1张主要图片**。

## 实际输出

从目录结构看，可能生成了：
- `Image_0_0_####_0_0_0_0001_0.png` - 格式错误的文件（导致解析错误）
- `Image_0010001.png` - 正常格式
- `Image_0_0_0001_0.exr` - EXR格式

## 如何控制输出数量

### 只生成1张PNG图片（当前设置）

```python
passes_to_save = [("Image", "Image")]
```

### 生成多通道图片

```python
passes_to_save = [
    ("Image", "Image"),
    ("Depth", "Depth"),
    ("Normal", "Normal"),
]
```

### 生成多相机图片

如果有多个相机，每个相机会生成一张图片。

## 建议

如果只想生成1张图片，当前设置已经正确。如果生成了多张，可能是：
1. 有多个相机
2. 有多个通道配置
3. 有旧文件残留

## 检查方法

```bash
# 查看实际生成的文件
ls -lh /home/ubuntu/infinigen/outputs/full_test/*.png
ls -lh /home/ubuntu/infinigen/outputs/full_test/frames_render_*/Image_*.png
```

