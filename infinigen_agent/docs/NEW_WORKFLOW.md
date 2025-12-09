# 新的工作流程说明

## 概述

Agent 现在采用**优先静态资产，缺失再程序化生成**的策略来生成家具并应用颜色。

## 工作流程

### 1. 生成色彩方案
- 用户输入自然语言描述（如"生成一个北欧风的卧室"）
- 大模型分析并生成家具RGB颜色方案

### 2. 优先从静态资产导入（步骤1）
- Agent 首先尝试从 `infinigen/assets/static_assets/source/` 目录导入家具
- 支持的家具类型：
  - `Bed/` - 床
  - `Sofa/` - 沙发
  - `Chair/` - 椅子
  - `Table/` - 桌子
  - `Cabinet/` - 柜子
  - `Shelf/` - 书架
  - 等等...
- 对导入的静态资产**立即应用颜色**

### 3. 程序化生成缺失家具（步骤2）
- 对于静态资产目录中**缺失的家具类型**，使用程序化生成器生成
- 支持的家具类型：
  - 床：`BedFactory`
  - 沙发：`SofaFactory`
  - 椅子：`ChairFactory`, `OfficeChairFactory`, `BarChairFactory`
  - 桌子：`TableDiningFactory`, `CoffeeTableFactory`, `SideTableFactory`
  - 柜子：`SingleCabinetFactory`
  - 书架：`SimpleBookcaseFactory`
  - 书桌：`SimpleDeskFactory`
  - 等等...
- 对生成的家具**立即应用颜色**

### 4. 查找场景中已有对象（备用方案）
- 对于既不支持静态资产导入，也不支持程序化生成的家具类型
- 在场景中查找已有对象并应用颜色

## 优势

1. **质量优先**：静态资产通常是精心制作的模型，质量更高
2. **灵活补充**：程序化生成可以补充静态资产中缺失的家具
3. **自动应用颜色**：所有家具（无论是导入还是生成的）都会自动应用颜色
4. **智能选择**：系统自动判断使用哪种方式

## 使用示例

```bash
# 基本用法
python run_agent.py "生成一个北欧风的卧室" scene.blend

# 禁用程序化生成（只使用静态资产和场景中已有对象）
python run_agent.py "生成一个北欧风的卧室" scene.blend --no-procedural

# 禁用静态资产导入（只使用程序化生成和场景中已有对象）
python run_agent.py "生成一个北欧风的卧室" scene.blend --no-import-assets
```

## 配置选项

在 `agent.py` 的 `process_request` 方法中：

- `import_missing_assets=True`：是否导入静态资产（默认开启）
- `use_procedural_generation=True`：是否使用程序化生成（默认开启）
- `static_assets_root=None`：静态资产根目录（默认自动检测）

## 添加新的程序化生成支持

要添加新的家具类型支持，编辑 `procedural_furniture_generator.py`：

```python
FURNITURE_FACTORY_MAP = {
    # 添加新的映射
    "new_furniture": NewFurnitureFactory,
}
```

然后导入对应的Factory类。

## 注意事项

1. **位置设置**：程序化生成的家具默认位置在原点 `(0, 0, 0)`，可以根据场景布局调整
2. **随机种子**：每次生成使用随机种子，确保家具变体多样性
3. **性能**：程序化生成比静态资产导入慢，但提供了更多变体
4. **兼容性**：确保在 Blender 环境中运行（需要 `bpy` 模块）
