# 校正需求说明

## 问题

如果使用 `save_all_passes=True` 时，Infinigen 会直接输出 PNG，那么是否还需要 tone mapping 和 gamma 校正？

## 答案：取决于情况

### ✅ 情况 1：使用 `save_all_passes=True`（推荐）

**不需要校正！**

- Infinigen 的 compositor 会处理图像
- Blender 的 PNG 输出节点会自动应用 sRGB 转换（包括 gamma 校正）
- 输出的 PNG 已经是正确的 sRGB 空间
- 代码会直接复制 PNG，**跳过所有校正**

```python
# scene_renderer.py 中的逻辑
if source_file.suffix.lower() == '.png':
    # 直接复制，不需要任何校正
    shutil.copy2(source_file, output_path)
```

### ⚠️ 情况 2：转换现有的 EXR 文件

**需要校正！**

`convert_exr_to_png.py` 是用来转换**现有的 EXR 文件**的：
- EXR 是线性空间的 HDR 格式
- 需要 tone mapping（HDR → LDR）
- 需要 gamma 校正（线性 → sRGB）
- **这些校正仍然需要**

## 总结

| 场景 | 文件格式 | 需要校正？ |
|------|---------|-----------|
| `save_all_passes=True` | PNG（直接输出） | ❌ **不需要** |
| 转换现有 EXR | EXR → PNG | ✅ **需要** |

## 代码逻辑

### scene_renderer.py

```python
if source_file.suffix.lower() == '.png':
    # PNG 已经处理过了，直接复制
    shutil.copy2(source_file, output_path)
    # 不需要任何校正！
    
elif source_file.suffix.lower() == '.exr':
    # EXR 需要转换和校正
    # ... tone mapping 和 gamma 校正 ...
```

### convert_exr_to_png.py

```python
# 这个脚本专门用来转换 EXR，所以总是需要校正
# 因为 EXR 是线性 HDR 格式
exr_image = read_exr(...)
# ... tone mapping ...
# ... gamma 校正 ...
save_png(...)
```

## 结论

- **`scene_renderer.py`**：如果找到 PNG，不需要校正（直接复制）
- **`convert_exr_to_png.py`**：仍然需要校正（因为它是用来转换 EXR 的）

**所以 `convert_exr_to_png.py` 中的校正代码仍然有用**，因为：
1. 它是独立工具，用于转换 EXR 文件
2. 用户可能手动转换 EXR 文件
3. 某些情况下可能只有 EXR 文件可用

