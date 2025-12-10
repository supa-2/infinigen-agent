# 自动生成场景功能说明

## 功能概述

现在 Infinigen Agent 支持从用户输入自动生成场景，无需手动准备场景文件。整个流程包括：

1. **自动生成场景**：调用 Infinigen 的 `generate_indoors` 命令生成 3D 场景
2. **应用颜色方案**：根据用户描述生成并应用家具颜色
3. **渲染输出**：生成图片或视频

## 使用方法

### 基本用法

```bash
cd /home/ubuntu/infinigen/infinigen_agent
python run_agent.py --auto-generate --output-folder /tmp/my_scene "生成一个北欧风格的卧室"
```

### 参数说明

- `--auto-generate`: 启用自动生成场景功能
- `--output-folder`: 指定场景输出文件夹（必需）
- `--seed`: 随机种子（可选，默认 0）
- `--infinigen-root`: Infinigen 根目录路径（可选，会自动检测）
- `--generate-timeout`: 生成超时时间（秒，可选）

### 完整示例

```bash
# 生成场景并渲染图片
python run_agent.py \
    --auto-generate \
    --output-folder /tmp/nordic_bedroom \
    --seed 42 \
    "生成一个北欧风格的卧室，使用浅灰色和白色"

# 生成场景并渲染视频
python run_agent.py \
    --auto-generate \
    --output-folder /tmp/modern_living_room \
    --render-video \
    "生成一个现代风格的客厅，使用深蓝色沙发和浅色地板"
```

## 工作流程

1. **场景生成阶段**
   - 调用 `infinigen_examples.generate_indoors`
   - 使用 `coarse` 任务快速生成场景结构
   - 输出 `.blend` 场景文件

2. **颜色方案生成**
   - 使用 LLM 分析用户描述
   - 生成家具颜色方案（JSON 格式）

3. **颜色应用**
   - 解析颜色方案
   - 在场景中查找对应家具
   - 应用颜色材质

4. **渲染输出**
   - 渲染单张图片或视频序列
   - 保存到指定输出目录

## 输出结构

```
/tmp/my_scene/
├── scene.blend              # 生成的场景文件
├── assets/                  # 场景资源
├── renders/                 # 渲染输出
│   ├── images/             # 图片输出
│   └── videos/             # 视频输出
└── logs/                   # 日志文件
```

## 注意事项

1. **首次使用**：确保已安装 Infinigen 的 terrain 依赖：
   ```bash
   cd /home/ubuntu/infinigen
   pip install .[terrain]
   ```

2. **编译要求**：如果遇到 `marching_cubes` 相关错误，需要编译 Cython 扩展：
   ```bash
   export INFINIGEN_INSTALL_TERRAIN=True
   export INFINIGEN_MINIMAL_INSTALL=False
   python setup.py build_ext --inplace
   ```

3. **生成时间**：场景生成可能需要几分钟时间，请耐心等待

4. **输出路径**：确保输出文件夹路径有写入权限

## 故障排除

详见 `docs/TROUBLESHOOTING.md`

