# 故障排查指南

## 常见错误及解决方案

### 1. Terrain 相关错误

#### 错误1: 缺少 landlab 模块

**错误信息:**
```
ImportError: landlab import failed for terrain snowfall simulation
 original error: No module named 'landlab'
You may need to install terrain dependencies via `pip install .[terrain]`
```

**解决方案:**

```bash
cd /home/ubuntu/infinigen
conda activate infinigen
pip install .[terrain]
```

#### 错误2: 缺少编译的共享库

**错误信息:**
```
OSError: /home/ubuntu/infinigen/infinigen/terrain/lib/cpu/elements/waterbody.so: cannot open shared object file: No such file or directory
```

**原因:**
Infinigen 的 terrain 模块需要编译 C++ 共享库，但当前环境中缺少这些库文件。

**解决方案:**

```bash
cd /home/ubuntu/infinigen
bash scripts/install/compile_terrain.sh
```

#### 完整安装 Terrain 依赖（推荐）

如果遇到 terrain 相关问题，建议完整安装所有依赖：

```bash
cd /home/ubuntu/infinigen
conda activate infinigen

# 安装 Python 依赖
pip install .[terrain]

# 编译 C++ 库
bash scripts/install/compile_terrain.sh
```

#### 方案2: 使用已有的场景文件

如果不需要自动生成场景，可以使用已有的场景文件：

```bash
python run_agent.py "生成一个北欧风的卧室" \
    ../outputs/hello_room/coarse/scene.blend \
    --render-image
```

#### 方案3: 检查 Infinigen 安装

确保 Infinigen 已正确安装：

```bash
cd /home/ubuntu/infinigen
conda activate infinigen
python -m infinigen_examples.generate_indoors --help
```

### 2. 场景生成器未初始化

**错误信息:**
```
错误: 场景生成器未初始化，无法自动生成场景
```

**解决方案:**

手动指定 Infinigen 根目录：

```bash
python run_agent.py "生成一个北欧风的卧室" \
    --auto-generate \
    --output-folder /tmp/test_room \
    --infinigen-root /home/ubuntu/infinigen \
    --render-image
```

### 3. vLLM 连接失败

**错误信息:**
```
无法从大模型获取响应
```

**解决方案:**

1. 检查 vLLM 服务是否运行：
```bash
ps aux | grep vllm
```

2. 检查 API 配置：
```bash
cat config/api_config.py
```

3. 测试连接：
```bash
python test_vllm.py
```

### 4. 颜色解析失败

**错误信息:**
```
未能解析出颜色信息
```

**解决方案:**

1. 检查大模型输出格式
2. 查看颜色解析器日志
3. 尝试更明确的用户请求，例如：
   - "生成一个北欧风的卧室，床是白色，床头柜是浅木色"
   - "生成一个现代简约风格的客厅，沙发是灰色，茶几是深色"

### 5. 渲染失败

**错误信息:**
```
渲染失败
```

**解决方案:**

1. 检查 Blender 环境是否正确配置
2. 检查场景文件是否存在
3. 尝试降低分辨率：
```bash
--resolution 640 480
```

### 6. 场景文件找不到

**错误信息:**
```
场景文件不存在
```

**解决方案:**

1. 检查文件路径是否正确
2. 确认文件扩展名是 `.blend`
3. 使用绝对路径而不是相对路径

## 环境检查清单

在运行自动生成场景功能前，请确认：

- [ ] Infinigen 已正确安装
- [ ] Conda 环境已激活 (`conda activate infinigen`)
- [ ] Terrain 模块已编译（如果使用 terrain）
- [ ] vLLM 服务正在运行
- [ ] 有足够的磁盘空间（场景生成会产生大量文件）
- [ ] 有足够的系统资源（CPU、内存）

## 获取帮助

如果以上方案都无法解决问题，请：

1. 检查完整的错误日志
2. 确认 Infinigen 版本和配置
3. 查看 Infinigen 官方文档
4. 检查系统依赖是否完整

## 快速测试

运行以下命令进行快速测试：

```bash
# 1. 测试 vLLM 连接
python test_vllm.py

# 2. 测试颜色解析
python test_color_parser.py

# 3. 测试使用已有场景文件（不生成场景）
python run_agent.py "生成一个北欧风的卧室" \
    ../outputs/hello_room/coarse/scene.blend \
    --render-image \
    --resolution 640 480
```

如果步骤3成功，说明 Agent 功能正常，问题在于场景生成部分。
