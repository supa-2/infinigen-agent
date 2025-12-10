# 默认行为说明

## 默认设置

**`save_all_passes=True` 现在是默认值！**

这意味着：
- ✅ 默认保存所有渲染通道（像官方命令一样）
- ✅ 直接输出 PNG 格式（不需要 EXR 转换）
- ✅ 更快、更简单、文件更小

## 使用方式

### 默认行为（推荐）

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("scene.blend")
# 默认 save_all_passes=True，直接输出 PNG
png_path = renderer.render_image("output.png")
```

**输出：**
- 主图像：`output.png`（PNG，直接输出，无需转换）
- 所有通道：`output.png` 所在目录的 `frames/` 子目录

### 只保存最终图像

如果你只需要最终图像，可以设置：

```python
renderer.render_image(
    "output.png",
    save_all_passes=False  # 只保存最终图像
)
```

## 优势

### ✅ 默认 `save_all_passes=True` 的好处

1. **直接输出 PNG**
   - 不需要 EXR → PNG 转换
   - 更快
   - 文件更小（PNG 约 1.4M，EXR 约 11M）

2. **完整的渲染数据**
   - 像官方命令一样保存所有通道
   - 可以用于后期合成、分析等

3. **更简单**
   - 不需要考虑格式转换
   - 代码逻辑更清晰

## 代码变化

### 之前

```python
# 默认只保存最终图像
renderer.render_image("output.png")  # 可能只有 EXR，需要转换
```

### 现在

```python
# 默认保存所有通道，直接输出 PNG
renderer.render_image("output.png")  # 直接 PNG，无需转换
```

## 性能对比

| 方式 | 输出格式 | 需要转换？ | 文件数 | 总大小 |
|------|---------|-----------|--------|--------|
| 旧默认 | EXR | ✅ 需要 | 1 个 | ~11M |
| 新默认 | PNG | ❌ 不需要 | 15+ 个 | ~20M（但更实用） |

## 注意事项

1. **文件数量**：保存所有通道会生成更多文件
2. **存储空间**：虽然单个 PNG 更小，但总文件数更多
3. **EXR 转换**：只有在找不到 PNG 时才会转换 EXR（这种情况很少见）

## 总结

**默认行为已优化：**
- ✅ `save_all_passes=True`（默认）
- ✅ 直接输出 PNG（无需转换）
- ✅ 完整的渲染数据（像官方命令）

**如果你只需要最终图像：**
- 设置 `save_all_passes=False`

