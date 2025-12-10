# PNG 直接输出说明

## 好消息！✅

**当使用 `save_all_passes=True` 时，Infinigen 会直接输出 PNG 格式，不需要转换！**

## 原因

从代码分析：

1. **Infinigen 的 compositor 配置**：
   - 创建两个输出节点：PNG 和 EXR
   - 默认使用 PNG（`saving_ground_truth=False` 时）
   - 同时也会输出 EXR（作为备份）

2. **官方命令的输出**：
   - 每个通道都有 **PNG 和 EXR 两个文件**
   - PNG 是主要输出，EXR 是备份

3. **我们的代码优化**：
   - 优先查找 PNG 文件
   - 如果找到 PNG，直接使用，**不需要转换**
   - 只有在找不到 PNG 时才转换 EXR

## 输出格式

使用 `save_all_passes=True` 后：

```
frames/
  └── Image/
      └── camera_0/
          ├── Image_0_0_0001_0.png  ✅ 直接输出，不需要转换
          └── Image_0_0_0001_0.exr   (备份，通常不需要)
```

## 性能优势

- ✅ **更快**：不需要 EXR → PNG 转换
- ✅ **更简单**：直接使用 PNG
- ✅ **更小**：PNG 文件比 EXR 小很多（1.4M vs 11M）

## 代码逻辑

```python
# 优先查找 PNG
rendered_files = list(image_dir.glob("Image_*.png"))

if rendered_files:
    # 找到 PNG，直接使用，不需要转换！
    source_file = rendered_files[0]
    shutil.copy2(source_file, output_path)
else:
    # 没找到 PNG，才查找 EXR 并转换
    rendered_files = list(image_dir.glob("Image_*.exr"))
    if rendered_files:
        # 转换 EXR → PNG
        ...
```

## 总结

| 情况 | 输出格式 | 需要转换？ |
|------|---------|-----------|
| `save_all_passes=True` | PNG（直接） | ❌ 不需要 |
| 默认（只 Image） | 可能是 EXR | ✅ 需要转换 |

**所以你的理解是对的！** 使用 `save_all_passes=True` 时，Infinigen 会直接输出 PNG，我们的代码会优先使用 PNG，不需要转换。

