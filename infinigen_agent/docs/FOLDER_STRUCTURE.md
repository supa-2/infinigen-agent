# Infinigen 文件夹结构说明

## 问题：为什么 agent 生成的文件夹结构和原本程序化指令生成的不一样？

### Infinigen 原生命令的文件夹结构

当直接使用 Infinigen 原生命令生成场景时：

```bash
python -m infinigen_examples.generate_indoors \
    --output_folder /path/to/output \
    -s seed \
    -t coarse
```

**生成的文件夹结构：**
```
output_folder/
├── coarse/              # 根据 task 参数创建的子目录
│   ├── scene.blend      # 场景文件
│   ├── frames/          # 渲染输出（如果执行了渲染任务）
│   ├── assets/          # 生成的资产
│   └── ...
├── pipeline_coarse.csv
└── ...
```

### Agent 的文件夹结构

Agent 调用 `generate_indoors` 时，传入的 `output_folder` 是用户指定的路径，但 `generate_indoors` 内部会根据 `task` 参数自动创建子目录。

**Agent 生成的文件夹结构：**
```
用户指定的 output_folder/
├── coarse/              # Infinigen 自动创建（因为 task="coarse"）
│   ├── scene.blend      # 场景文件在这里
│   ├── frames/          # 渲染输出
│   └── ...
└── ...
```

### 原因分析

1. **Infinigen 的设计**：
   - `execute_tasks.main()` 会根据 `task` 参数创建对应的子目录
   - 如果 `task="coarse"`，会在 `output_folder` 下创建 `coarse/` 子目录
   - 如果 `task="render"`，会在 `output_folder` 下创建 `render/` 子目录

2. **Agent 的实现**：
   - Agent 直接调用 `generate_indoors`，传入用户指定的 `output_folder`
   - 但 `generate_indoors` 内部会创建 `coarse/` 子目录
   - 所以场景文件实际在 `output_folder/coarse/scene.blend`

### 解决方案

Agent 的 `_find_scene_file()` 方法已经考虑了这种情况，会递归搜索 `.blend` 文件：

```python
possible_paths = [
    output_folder / "scene.blend",           # 直接在根目录
    output_folder / "coarse" / "scene.blend", # 在 coarse 子目录（实际位置）
    output_folder / "outputs" / "scene.blend",
]
```

### 建议

1. **统一文件夹结构**：Agent 应该明确告知用户场景文件的位置
2. **文档说明**：在生成场景后，明确输出场景文件的完整路径
3. **可选优化**：如果用户指定了 `output_folder`，可以考虑在生成后移动文件到根目录（但这可能影响 Infinigen 的其他功能）

### 当前行为

- ✅ Agent 能够正确找到场景文件（通过递归搜索）
- ✅ 场景文件位置：`output_folder/coarse/scene.blend`
- ⚠️ 用户可能期望场景文件在 `output_folder/scene.blend`
