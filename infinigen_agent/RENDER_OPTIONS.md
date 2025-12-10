# 渲染选项说明

## 两种模式对比

### 模式 1：只保存最终图像（默认）✅ 推荐

**特点：**
- ✅ 更快（文件更少）
- ✅ 文件更少（只有 1 个文件）
- ✅ 存储空间更小
- ⚠️ 可能需要 EXR 转换（如果 Infinigen 输出 EXR）

**使用方式：**
```python
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("scene.blend")
# 默认只保存最终图像
png_path = renderer.render_image("output.png")
```

**输出：**
- 只有 1 个文件：`output.png`

### 模式 2：保存所有通道

**特点：**
- ✅ 直接输出 PNG（不需要转换）
- ✅ 完整的渲染数据（可用于后期合成）
- ⚠️ 文件更多（14+ 个文件）
- ⚠️ 存储空间更大

**使用方式：**
```python
renderer = SceneRenderer("scene.blend")
# 保存所有通道
png_path = renderer.render_image("output.png", save_all_passes=True)
```

**输出：**
- 主图像：`output.png`
- 所有通道：`output.png` 所在目录的 `frames/` 子目录（14+ 个文件）

## 性能对比

| 模式 | 文件数 | 总大小 | 需要转换？ | 总时间 |
|------|--------|--------|-----------|--------|
| 只保存最终图像 | 1 个 | ~2-3 MB | 可能（如果 EXR） | 渲染 + 0-3 秒 |
| 保存所有通道 | 15+ 个 | ~20-30 MB | ❌ 不需要 | 渲染 + 1-2 秒 |

## 选择建议

### 使用"只保存最终图像"（默认）如果：
- ✅ 只需要最终渲染效果
- ✅ 想要更少的文件
- ✅ 存储空间有限
- ✅ 不需要后期合成

### 使用"保存所有通道"如果：
- ✅ 需要完整的渲染数据
- ✅ 想要直接 PNG（不需要转换）
- ✅ 需要后期合成或分析
- ✅ 想要与官方命令一致的行为

## 代码示例

### 只保存最终图像（默认）

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("scene.blend")
# 默认只保存最终图像
png_path = renderer.render_image("output.png")
# 或者显式设置
png_path = renderer.render_image("output.png", save_all_passes=False)
```

### 保存所有通道

```python
renderer = SceneRenderer("scene.blend")
# 保存所有通道
png_path = renderer.render_image("output.png", save_all_passes=True)
```

### 自定义通道

```python
renderer = SceneRenderer("scene.blend")
# 只保存 Image 和 AO 通道
png_path = renderer.render_image(
    "output.png",
    passes_to_save=["Image", "AO"]
)
```

## 总结

**默认行为已优化为：只保存最终图像**
- ✅ 更快
- ✅ 文件更少
- ✅ 更实用（大多数情况下只需要最终图像）

**如果需要所有通道，设置 `save_all_passes=True`**

