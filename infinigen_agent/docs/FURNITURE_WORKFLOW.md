# 家具生成工作流程

## 概述

Agent 现在采用**优先静态资产，缺失则程序化生成**的策略来生成家具并应用颜色。

## 工作流程

### 完整流程

```
用户输入 → 大模型生成色彩方案 → 解析颜色
    ↓
步骤1: 优先从静态资产目录导入家具并应用颜色
    ↓
步骤2: 对静态资产中缺失的家具，使用程序化生成器生成并应用颜色
    ↓
步骤3: 对于不支持程序化生成的家具，在场景中查找已有对象并应用颜色
    ↓
保存最终场景
```

### 详细步骤

#### 步骤1: 静态资产优先导入

1. **检查静态资产目录**
   - 路径：`infinigen/assets/static_assets/source/`
   - 根据家具类型查找对应的文件夹（如 `Chair/`, `Sofa/`, `Bed/` 等）

2. **导入静态资产**
   - 从对应文件夹中随机选择一个资产文件（.glb, .obj, .fbx 等）
   - 导入到当前场景中

3. **立即应用颜色**
   - 对导入的静态资产立即应用大模型生成的RGB颜色
   - 记录已处理的家具类型

**优点**：
- 静态资产通常是高质量、完整的3D模型
- 导入速度快
- 模型质量稳定

#### 步骤2: 程序化生成缺失家具

对于静态资产目录中**不存在**的家具类型：

1. **检查是否支持程序化生成**
   - 查看 `ProceduralFurnitureGenerator` 是否支持该家具类型
   - 支持的家具类型包括：
     - 座椅类：bed, sofa, chair, armchair, office_chair, bar_chair
     - 桌子类：table, dining_table, coffee_table, side_table, cocktail_table
     - 柜子类：cabinet, bookshelf, bookcase, shelf, desk, tv_stand

2. **程序化生成**
   - 使用 Infinigen 的 Factory 类生成家具
   - 每次生成都有随机变化，保证多样性

3. **应用颜色**
   - 对生成的家具立即应用颜色

**优点**：
- 可以生成静态资产中没有的家具
- 每次生成都有变化，增加场景多样性
- 完全程序化，无需外部模型文件

#### 步骤3: 场景中已有对象

对于**不支持程序化生成**且**静态资产中也没有**的家具：

1. **在场景中查找**
   - 根据家具类型名称在场景中搜索匹配的对象
   - 支持中英文关键词匹配

2. **应用颜色**
   - 对找到的对象应用颜色

## 使用示例

### 基本用法

```bash
python run_agent.py "生成一个北欧风的卧室" scene.blend
```

**工作流程**：
1. 大模型生成色彩方案（床、床头柜、沙发等）
2. 优先从静态资产导入：`Bed/`, `Sofa/` 等文件夹中的模型
3. 如果 `nightstand` 在静态资产中不存在，使用程序化生成器生成
4. 对不支持程序化生成的家具（如 `curtain`），在场景中查找已有对象

### 禁用程序化生成

```bash
python run_agent.py "生成一个北欧风的卧室" scene.blend --no-procedural
```

**工作流程**：
1. 优先从静态资产导入
2. 缺失的家具只在场景中查找已有对象（不使用程序化生成）

### 禁用静态资产导入

```bash
python run_agent.py "生成一个北欧风的卧室" scene.blend --no-import-assets
```

**工作流程**：
1. 跳过静态资产导入
2. 直接使用程序化生成或场景中已有对象

## 家具类型映射

### 静态资产文件夹映射

| 家具类型（LLM输出） | 静态资产文件夹 | 是否支持程序化生成 |
|-------------------|--------------|------------------|
| `bed` | `Bed/` | ✅ Yes (BedFactory) |
| `sofa`, `couch` | `Sofa/` | ✅ Yes (SofaFactory) |
| `chair`, `dining_chair` | `Chair/` | ✅ Yes (ChairFactory) |
| `table`, `dining_table` | `Table/` | ✅ Yes (TableDiningFactory) |
| `coffee_table` | `Table/` | ✅ Yes (CoffeeTableFactory) |
| `cabinet` | `Cabinet/` | ✅ Yes (SingleCabinetFactory) |
| `bookshelf`, `bookcase` | `Shelf/` | ✅ Yes (SimpleBookcaseFactory) |
| `desk` | - | ✅ Yes (SimpleDeskFactory) |
| `nightstand` | `Bed/` | ❌ No |
| `curtain`, `curtains` | `ceilingHanging/` | ❌ No |
| `rug`, `carpet` | `Decoration/` | ❌ No |
| `lamp` | `Lighting/` | ❌ No |

## 处理优先级

1. **静态资产**（最高优先级）
   - 如果静态资产目录中存在对应文件夹和文件，优先使用

2. **程序化生成**（中等优先级）
   - 如果静态资产中不存在，且支持程序化生成，则使用程序化生成器

3. **场景中已有对象**（最低优先级）
   - 如果前两者都不可用，则在场景中查找已有对象

## 日志输出示例

```
============================================================
Infinigen 智能体开始处理请求
============================================================
正在向大模型请求色彩方案...
大模型生成的色彩方案:
1. bed: (250, 250, 250)
2. sofa: (200, 200, 200)
3. chair: (192, 192, 192)
4. nightstand: (222, 184, 135)

解析到 4 个家具颜色

============================================================
步骤1: 优先从静态资产目录导入家具并应用颜色
============================================================

正在导入 bed 从: /path/to/Bed/
✓ 成功导入资产: bed_standard.glb
✓ 成功导入 1 个静态资产

正在对导入的静态资产应用颜色...
  ✓ bed: 已导入 1 个对象并应用颜色

正在导入 sofa 从: /path/to/Sofa/
✓ 成功导入资产: sofa_standard.glb
  ✓ sofa: 已导入 1 个对象并应用颜色

⚠ 未找到 nightstand 的资产文件夹: /path/to/Nightstand/

找到 2 个需要处理的家具类型（静态资产中缺失）:
  - chair
  - nightstand

============================================================
步骤2: 对缺失的家具，使用程序化生成器生成并应用颜色
============================================================

使用程序化生成器生成 1 个家具类型:
  ✓ chair: 已生成并应用颜色

在场景中查找 1 个已有对象并应用颜色:
  ✓ nightstand: 找到 1 个对象并应用颜色

============================================================
✓ 处理完成！
输出文件: scene_colored.blend
============================================================
```

## 配置选项

### 命令行参数

- `--import-assets` / `--no-import-assets`: 是否导入静态资产（默认启用）
- `--procedural` / `--no-procedural`: 是否使用程序化生成（默认启用）
- `--static-assets-root`: 指定静态资产根目录

### 代码中配置

```python
from src.agent import InfinigenAgent

agent = InfinigenAgent()

output = agent.process_request(
    user_request="生成一个北欧风的卧室",
    scene_path="scene.blend",
    import_missing_assets=True,      # 启用静态资产导入
    use_procedural_generation=True,  # 启用程序化生成
    static_assets_root=None          # 使用默认路径
)
```

## 注意事项

1. **静态资产优先级最高**：如果静态资产目录中存在对应家具，会优先使用，不会使用程序化生成

2. **程序化生成位置**：目前程序化生成的家具默认位置在原点 `(0, 0, 0)`，可能需要手动调整位置

3. **场景布局**：建议在生成场景后，根据房间布局调整家具位置

4. **颜色应用**：所有导入或生成的家具都会立即应用大模型生成的RGB颜色

5. **性能考虑**：
   - 静态资产导入：快速（毫秒级）
   - 程序化生成：较慢（秒级，取决于家具复杂度）
   - 场景查找：快速（毫秒级）

## 扩展支持

### 添加新的静态资产

1. 在 `infinigen/assets/static_assets/source/` 下创建新文件夹
2. 将资产文件放入文件夹
3. 更新 `static_asset_importer.py` 中的 `furniture_folder_map`

### 添加新的程序化生成支持

1. 在 `procedural_furniture_generator.py` 中导入新的 Factory 类
2. 在 `FURNITURE_FACTORY_MAP` 中添加映射
