# 光照改进说明

## 问题
渲染图的光照看起来有问题，可能过暗、过亮或颜色不自然。

## 原因分析

### 1. **缺少 Gamma 校正**
- EXR 格式使用**线性颜色空间**（linear color space）
- PNG 格式需要 **sRGB 颜色空间**
- 如果不进行 gamma 校正，图像会看起来过暗

### 2. **Tone Mapping 不够好**
- 简单的 Reinhard tone mapping 可能丢失细节
- 需要更温和的映射以保留高光细节

### 3. **负值处理**
- EXR 中可能有微小的负值（浮点误差）
- 需要修正为 0

## 改进方案

### ✅ 已实现的改进

1. **Gamma 校正**
   ```python
   # 应用 gamma 2.2（标准 sRGB）
   exr_image = np.power(exr_image, 1.0 / 2.2)
   ```

2. **改进的 Tone Mapping**
   ```python
   # 更温和的 Reinhard，保留更多细节
   exr_image = exr_image / (1 + exr_image * 0.8)
   ```

3. **负值修正**
   ```python
   # 修正浮点误差导致的负值
   exr_image = np.maximum(exr_image, 0)
   ```

## 使用方法

### 方法 1：使用改进后的转换脚本

```bash
conda activate infinigen
python infinigen_agent/convert_exr_to_png.py image.exr -o output.png
```

### 方法 2：使用渲染器（自动应用改进）

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("scene.blend")
png_path = renderer.render_image("output.png")  # 自动应用改进
```

## 技术细节

### 颜色空间转换流程

```
EXR (线性空间) 
  → Tone Mapping (HDR → LDR)
  → Gamma 校正 (线性 → sRGB)
  → PNG (sRGB 空间)
```

### Gamma 校正原理

- **线性空间**：物理上正确的亮度值
- **sRGB 空间**：人眼感知的亮度值
- **Gamma 2.2**：标准 sRGB gamma 值
- **公式**：`sRGB = linear^(1/2.2)`

### Tone Mapping 参数

- **系数 0.8**：调整映射曲线，保留更多高光细节
- 可以根据需要调整（0.6-1.0 范围）

## 进一步优化

如果需要进一步调整光照，可以修改以下参数：

1. **Exposure（曝光）**
   ```python
   exposure = 1.2  # 增加曝光（更亮）
   exr_image = exr_image * exposure
   ```

2. **Tone Mapping 系数**
   ```python
   # 更温和（保留更多细节）
   exr_image = exr_image / (1 + exr_image * 0.6)
   
   # 更强烈（更强对比）
   exr_image = exr_image / (1 + exr_image * 1.0)
   ```

3. **Gamma 值**
   ```python
   # 标准 sRGB
   gamma = 2.2
   
   # 更亮
   gamma = 2.0
   
   # 更暗
   gamma = 2.4
   ```

## 测试

重新转换你的图片，看看光照是否改善：

```bash
conda activate infinigen
python infinigen_agent/convert_exr_to_png.py \
  outputs/test_langchain_1765279816/frames/Image/camera_0/Image_0_0_0001_0.exr \
  -o outputs/test_langchain_1765279816/rendered_image_improved.png
```

对比新旧图片，应该能看到：
- ✅ 更自然的亮度
- ✅ 更好的高光细节
- ✅ 更准确的颜色

