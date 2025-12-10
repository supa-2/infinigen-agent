# 预生成模板池功能说明

## 功能概述

预生成模板池（Template Pool）是一个优化方案，通过预先生成通用场景模板，大幅缩短场景生成的响应时间。

### 工作原理

1. **预生成阶段**：后台批量生成各种房间类型的场景模板（仅几何体，无特定材质）
2. **运行时检索**：Agent 根据用户输入自动检索合适的模板
3. **快速应用**：直接使用模板，只执行改色和渲染步骤

### 性能提升

- **传统方式**：场景生成（5-10分钟）+ 改色（1分钟）+ 渲染（1分钟）= **7-12分钟**
- **使用模板池**：模板检索（<1秒）+ 改色（1分钟）+ 渲染（1分钟）= **2-3分钟**
- **性能提升**：响应时间缩短 **70-80%**

## 使用方法

### 1. 生成模板池

首先需要预生成模板池。可以使用批量生成脚本：

```bash
cd /home/ubuntu/infinigen/infinigen_agent

# 生成所有主要房间类型的模板（每个类型15个）
python tools/generate_template_pool.py --all

# 只生成卧室模板（10个）
python tools/generate_template_pool.py --room-type Bedroom --count 10

# 生成完整房屋模板（5个）
python tools/generate_template_pool.py --whole-home --count 5

# 生成所有模板（包括完整房屋）
python tools/generate_template_pool.py --all --whole-home-count 5

# 查看模板池统计信息
python tools/generate_template_pool.py --list
```

### 2. 使用模板池

Agent 默认启用模板池功能。运行时会自动检索并使用模板：

```bash
# Agent 会自动使用模板池（如果启用）
python src/langchain_agent.py "生成一个北欧风格的卧室"
```

如果找到匹配的模板，Agent 会显示：

```
🔍 正在从模板池检索可用模板...
✓ 找到可用模板: bedroom_01
   房间类型: Bedroom
   模板文件: /path/to/templates/...
   文件大小: 25.43 MB
⚡ 使用模板跳过场景生成步骤（节省 5-10 分钟）
```

### 3. 禁用模板池

如果需要禁用模板池（强制生成新场景）：

```python
from src.langchain_agent import LangChainInfinigenAgent

agent = LangChainInfinigenAgent(
    use_template_pool=False  # 禁用模板池
)
```

## 支持的房间类型

根据官方文档，以下房间类型有完整的家具约束支持：

- **Bedroom**（卧室）
- **LivingRoom**（客厅）
- **Kitchen**（厨房）
- **Bathroom**（浴室）
- **DiningRoom**（餐厅）

此外，还支持生成**完整房屋**（WholeHome）模板。

## 模板池结构

模板池目录结构：

```
infinigen_agent/templates/
├── templates_metadata.json     # 模板元数据文件
├── generating/                 # 临时生成目录
│   ├── bedroom_01/
│   ├── kitchen_01/
│   └── ...
└── ...                        # 其他生成的模板文件
```

## 参数说明

### 批量生成脚本参数

- `--all`: 生成所有主要房间类型的模板
- `--room-type`: 指定房间类型（Bedroom, Kitchen, LivingRoom, Bathroom, DiningRoom）
- `--whole-home`: 生成完整房屋模板
- `--count`: 每个类型的模板数量（默认: 5）
- `--whole-home-count`: 完整房屋模板数量（默认: 5）
- `--pool-root`: 模板池根目录（默认: infinigen_agent/templates）
- `--timeout`: 每个房间场景的超时时间（秒，默认: 900 = 15分钟）
- `--timeout-home`: 每个完整房屋场景的超时时间（秒，默认: 1800 = 30分钟）
- `--no-ultra-fast`: 不使用 ultra_fast_solve.gin（使用 fast_solve.gin 代替）
- `--list`: 列出当前模板池中的所有模板

### Agent 参数

- `use_template_pool`: 是否使用模板池（默认: True）
- `template_pool_root`: 模板池根目录（默认: None，使用默认路径）

## 最佳实践

1. **预生成足够数量的模板**：每个房间类型建议生成 5-10 个模板，确保多样性
2. **使用超快配置**：批量生成时使用 `ultra_fast_solve.gin` 加快生成速度
3. **定期更新模板池**：可以定期重新生成模板，保持模板的新鲜度
4. **监控模板使用情况**：查看 Agent 返回的 `used_template` 字段，了解模板使用率

## 注意事项

1. **模板文件大小**：每个模板文件通常 20-50 MB，确保有足够的磁盘空间
2. **生成时间**：批量生成所有模板可能需要数小时，建议在后台运行
3. **模板复用**：模板会被复制到输出目录，原模板不会被修改
4. **向后兼容**：如果没有找到模板，Agent 会自动回退到直接生成场景

## 示例

### 完整工作流程示例

```bash
# 1. 生成模板池（建议在后台运行）
nohup python tools/generate_template_pool.py --all > template_generation.log 2>&1 &

# 2. 查看生成进度
tail -f template_generation.log

# 3. 查看模板池统计
python tools/generate_template_pool.py --list

# 4. 使用 Agent（自动使用模板池）
python src/langchain_agent.py "生成一个红色调的北欧卧室" \
    --output-folder outputs/my_bedroom
```

## 技术细节

### 模板检索逻辑

1. Agent 检测用户输入中的房间类型
2. 在模板池中查找匹配房间类型的模板
3. 如果有多个模板，优先选择最近创建的
4. 将模板复制到输出目录（保持原模板不变）

### 模板元数据

每个模板包含以下元数据：

- `template_id`: 模板唯一标识符
- `room_type`: 房间类型
- `scene_file`: 场景文件路径
- `seed`: 使用的随机种子
- `created_at`: 创建时间
- `file_size_mb`: 文件大小（MB）
- `description`: 可选描述

## 故障排除

### 问题：找不到模板

**原因**：模板池为空或没有对应房间类型的模板

**解决方案**：
```bash
# 生成对应房间类型的模板
python tools/generate_template_pool.py --room-type Bedroom --count 10
```

### 问题：模板文件不存在

**原因**：模板元数据中记录的路径已失效

**解决方案**：
```bash
# 重新生成模板池
python tools/generate_template_pool.py --all
```

### 问题：模板使用率低

**原因**：用户输入的房间类型与模板类型不匹配

**解决方案**：生成更多类型的模板，或检查房间类型检测逻辑

## 相关文档

- [自动生成场景功能](./AUTO_GENERATE.md)
- [快速开始指南](./QUICK_START.md)
- [Infinigen 官方文档 - HelloRoom](../docs/HelloRoom.md)

