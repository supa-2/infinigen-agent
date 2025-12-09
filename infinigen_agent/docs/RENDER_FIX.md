# 渲染错误修复说明

## 问题描述

渲染时出现错误：
```
ValueError: Couldnt parse s='Image_0_0_####_0_0_0_0001_0' with len(s_parts)=9
```

## 原因分析

`reorganize_old_framesfolder` 函数尝试解析frames文件夹中的文件名时，遇到了不符合预期格式的文件。

Infinigen期望的文件名格式应该是：
- `Image_cam_rig_resample_frame_subcam.png`
- 例如：`Image_0_0_0001_0.png`（5个部分）

但实际文件名是：
- `Image_0_0_####_0_0_0_0001_0`（9个部分）

## 修复方案

### 方案1: 使用临时目录（已实现）

使用带时间戳的临时目录，确保是全新的：

```python
frames_folder = output_dir / f"frames_render_{int(time.time())}"
```

**优点**:
- 避免与旧文件冲突
- 每次渲染使用新目录
- 渲染后可以清理

### 方案2: 清理旧文件

在渲染前清理不符合格式的文件。

### 方案3: 使用Blender内置渲染（备选）

如果Infinigen的render_image一直有问题，可以使用Blender的内置渲染功能。

## 当前实现

已修复为使用临时目录，应该可以避免这个问题。

## 测试

重新运行测试：

```bash
python run_agent.py "生成一个北欧风格的卧室" \
    --auto-generate \
    --output-folder /home/ubuntu/infinigen/outputs/full_test \
    --no-import-assets \
    --render-image \
    --resolution 1280 720
```

## 如果仍然失败

可以尝试使用Blender内置渲染（更简单但功能较少）：

```python
# 在scene_renderer.py中使用bpy.ops.render.render()
bpy.ops.render.render()
bpy.data.images['Render Result'].save_render(output_path)
```
