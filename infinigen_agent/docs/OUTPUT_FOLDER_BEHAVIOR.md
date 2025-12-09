# 输出文件夹行为说明

## 问题：重复运行会覆盖文件吗？

### Infinigen 原生行为

**是的，会覆盖！**

Infinigen 的 `generate_indoors` 命令会：
- ✅ 如果输出文件夹不存在，创建新文件夹
- ⚠️ **如果输出文件夹已存在，会覆盖其中的文件**
- ⚠️ 不会提示或警告，直接覆盖

### 示例

```bash
# 第一次运行
python -m infinigen_examples.generate_indoors --output_folder outputs/test -s 12345 -t coarse
# 生成: outputs/test/coarse/scene.blend

# 第二次运行相同命令
python -m infinigen_examples.generate_indoors --output_folder outputs/test -s 12345 -t coarse
# ⚠️ 会覆盖 outputs/test/coarse/scene.blend
```

## Agent 的改进

### 自动重命名机制（默认启用）

Agent 添加了 `auto_rename` 参数（默认 `True`），可以避免覆盖：

```python
generator = SceneGenerator()

# 方式1: 自动重命名（默认，推荐）
scene_file = generator.generate_scene(
    output_folder="outputs/test",
    seed="12345"
)
# 如果 outputs/test 已存在且包含场景文件
# 会自动重命名为: outputs/test_1234567890 (添加时间戳)

# 方式2: 允许覆盖（明确指定）
scene_file = generator.generate_scene(
    output_folder="outputs/test",
    seed="12345",
    auto_rename=False  # 允许覆盖已有文件
)
```

### 行为说明

| 情况 | auto_rename=True (默认) | auto_rename=False |
|------|------------------------|------------------|
| 文件夹不存在 | ✅ 创建新文件夹 | ✅ 创建新文件夹 |
| 文件夹存在但为空 | ✅ 使用现有文件夹 | ✅ 使用现有文件夹 |
| 文件夹存在且包含场景文件 | ✅ **自动重命名**（添加时间戳） | ⚠️ **覆盖已有文件** |

### 重命名规则

如果检测到输出文件夹已存在且包含场景文件，会自动添加时间戳：

```
原路径: outputs/test
重命名: outputs/test_1765212345  (时间戳: Unix timestamp)
```

## 使用建议

### 推荐做法

1. **使用不同的输出文件夹**（最安全）
   ```python
   generator.generate_scene(
       output_folder=f"outputs/test_{seed}",  # 根据 seed 命名
       seed="12345"
   )
   ```

2. **使用自动重命名**（默认）
   ```python
   generator.generate_scene(
       output_folder="outputs/test",
       seed="12345"
       # auto_rename=True 是默认值
   )
   ```

3. **明确允许覆盖**（如果确定要覆盖）
   ```python
   generator.generate_scene(
       output_folder="outputs/test",
       seed="12345",
       auto_rename=False  # 明确允许覆盖
   )
   ```

## 代码实现

### 检测逻辑

```python
# 检查输出文件夹是否已存在
if output_path.exists() and output_path.is_dir():
    # 检查是否包含场景文件
    existing_scene = self._find_scene_file(output_path)
    if existing_scene and auto_rename:
        # 自动重命名，添加时间戳
        timestamp = int(time.time())
        new_name = f"{output_path.name}_{timestamp}"
        output_path = output_path.parent / new_name
```

### 日志输出

- ✅ 自动重命名时会输出警告日志
- ⚠️ 允许覆盖时会输出警告日志

## 总结

| 方式 | 行为 | 推荐度 |
|------|------|--------|
| **Agent + auto_rename=True** | 自动重命名，避免覆盖 | ⭐⭐⭐⭐⭐ |
| **Agent + auto_rename=False** | 允许覆盖，和原生一致 | ⭐⭐⭐ |
| **原生命令** | 直接覆盖，无提示 | ⭐⭐ |

**推荐使用 Agent 的自动重命名功能**，这样可以：
- ✅ 避免意外覆盖
- ✅ 保留历史版本
- ✅ 更安全
