# Shell 命令方式实现

## 概述

Agent 现在支持两种方式调用 Infinigen：

1. **Python 子进程方式**（默认）：通过 Python subprocess 调用 Infinigen 模块
2. **Shell 命令方式**（可选）：直接使用 shell 命令或 shell 脚本

## 改进内容

### 1. Shell 命令字符串方式

`generate_scene()` 方法现在使用 shell 命令字符串而不是参数列表：

**之前（Python 列表方式）：**
```python
cmd = [
    sys.executable,
    '-m', 'infinigen_examples.generate_indoors',
    '--output_folder', str(output_path),
    '-s', str(seed),
    '-t', task
]
subprocess.run(cmd, ...)
```

**现在（Shell 命令方式）：**
```python
shell_cmd = 'python -m infinigen_examples.generate_indoors --output_folder "..." -s "..." -t "..."'
subprocess.run(shell_cmd, shell=True, ...)
```

**优势：**
- ✅ 更直观，命令可以直接复制到终端执行
- ✅ 更容易调试，可以看到完整的命令
- ✅ 可以使用 shell 的特性（环境变量、管道等）

### 2. 独立的 Shell 脚本

创建了 `scripts/generate_scene.sh` 脚本，可以直接调用：

```bash
./scripts/generate_scene.sh \
    --output-folder /path/to/output \
    -s seed \
    -t coarse \
    -g base disable/no_objects
```

**使用方法：**
```python
generator = SceneGenerator()
scene_file = generator.generate_scene(
    output_folder="/path/to/output",
    seed="12345",
    use_shell_script=True  # 使用 shell 脚本
)
```

## 使用方式

### 方式 1：默认 Shell 命令方式（推荐）

```python
from src.scene_generator import SceneGenerator

generator = SceneGenerator()
scene_file = generator.generate_scene(
    output_folder="/path/to/output",
    seed="12345",
    task="coarse"
)
# 自动使用 shell 命令字符串方式
```

### 方式 2：使用 Shell 脚本

```python
from src.scene_generator import SceneGenerator

generator = SceneGenerator()
scene_file = generator.generate_scene(
    output_folder="/path/to/output",
    seed="12345",
    task="coarse",
    use_shell_script=True  # 使用独立的 shell 脚本
)
```

### 方式 3：直接调用 Shell 脚本

```bash
cd /home/ubuntu/infinigen/infinigen_agent
./scripts/generate_scene.sh \
    --output-folder /path/to/output \
    -s 12345 \
    -t coarse \
    -g base disable/no_objects
```

## 优势对比

| 特性 | Python 列表方式 | Shell 命令方式 | Shell 脚本方式 |
|------|----------------|---------------|---------------|
| 可读性 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 可调试性 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 安全性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 灵活性 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 独立性 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 注意事项

1. **安全性**：使用 `shell=True` 时需要注意命令注入风险，但在这个场景中，所有参数都是内部控制的，相对安全。

2. **路径处理**：Shell 命令方式会自动处理包含空格的路径（添加引号）。

3. **环境变量**：Shell 命令方式可以更好地利用系统环境变量。

4. **错误处理**：两种方式的错误处理逻辑相同，都会捕获并报告错误。

## 未来改进

1. 添加更多配置选项到 shell 脚本
2. 支持并行生成多个场景
3. 添加进度监控和日志记录
4. 支持断点续传

