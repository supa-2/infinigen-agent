# EXR 转 PNG 转换测试说明

## 为什么需要转换？

### 问题：官方文档说能直接生成图片，为什么我这边只生成了 EXR？

**答案：**

1. **Infinigen 的渲染机制**：
   - Infinigen 使用 Blender Compositor 输出图片
   - 代码理论上会同时生成 PNG 和 EXR，但在实际运行中可能只生成 EXR
   - EXR 是 Infinigen 的**默认输出格式**（高动态范围，32位浮点数）

2. **EXR vs PNG**：
   - **EXR**：HDR 格式，32位浮点数，文件大，需要特殊软件查看
   - **PNG**：标准图片格式，8位整数，文件小，任何查看器都能打开

3. **官方命令的情况**：
   - 官方命令（`--task render`）理论上会生成 PNG
   - 但在某些配置下可能只生成 EXR
   - 或者官方文档中的"图片"指的是 EXR（EXR 也是图片格式）

4. **我们的解决方案**：
   - `scene_renderer.py` 已集成自动转换功能
   - 如果检测到 EXR，会自动转换为 PNG
   - 如果转换失败，会返回 EXR 文件路径

**详细说明请查看：`EXR_VS_PNG_EXPLANATION.md`**

## 测试脚本

已创建两个测试脚本：

1. **`test_exr_simple.py`** - 简单版本，直接测试转换功能
2. **`test_exr_conversion.py`** - 详细版本，包含完整的错误处理和诊断信息

## 使用方法

```bash
cd /home/ubuntu/infinigen
python3 infinigen_agent/test_exr_simple.py
```

## 测试内容

脚本会：
1. ✅ 检查 `imageio` 和 `numpy` 是否安装
2. ✅ 查找 EXR 文件：`outputs/test_langchain_1765279816/frames/Image/camera_0/Image_0_0_0001_0.exr`
3. ✅ 读取 EXR 文件并显示图像信息（形状、数据类型、值范围）
4. ✅ 转换为 uint8 格式（使用 tone mapping 如果值 > 1.0）
5. ✅ 处理通道数（只保留 RGB 3 个通道）
6. ✅ 保存为 PNG：`outputs/test_langchain_1765279816/rendered_image.png`

## 转换逻辑

### 1. 读取 EXR
```python
exr_image = imageio.imread(str(exr_path))
```

### 2. 转换为 uint8
- 如果最大值 <= 1.0：简单缩放 `* 255`
- 如果最大值 > 1.0：使用 Reinhard tone mapping `L_out = L_in / (1 + L_in)`

### 3. 处理通道
- 如果通道数 > 3：只保留前 3 个通道（RGB）
- 如果是灰度图：转换为 RGB

### 4. 保存 PNG
```python
imageio.imwrite(str(png_path), png_image)
```

## 预期输出

```
✅ 依赖库已安装
EXR 文件: outputs/test_langchain_1765279816/frames/Image/camera_0/Image_0_0_0001_0.exr
存在: True
✅ 找到 EXR 文件 (XX.XX MB)

读取 EXR...
✅ 读取成功
  形状: (1080, 1920, 3)
  类型: float32
  范围: 0.0000 - X.XXXX

转换...
✅ 转换完成
  形状: (1080, 1920, 3)
  类型: uint8

保存 PNG...
✅ PNG 保存成功: outputs/test_langchain_1765279816/rendered_image.png
  大小: XX.XX MB
```

## 如果测试失败

1. **缺少依赖库**：`pip install imageio imageio-ffmpeg`
2. **EXR 文件不存在**：检查路径是否正确
3. **读取失败**：检查 EXR 文件是否损坏
4. **转换失败**：检查图像数据类型和形状

## 集成到 scene_renderer.py

转换逻辑已经集成到 `scene_renderer.py` 的 `render_image` 方法中：
- 自动查找 EXR 文件
- 自动转换为 PNG
- 如果转换失败，返回 EXR 文件路径
