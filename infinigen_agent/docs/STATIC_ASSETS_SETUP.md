# 静态资产设置指南

根据 Infinigen 官方文档，导入外部静态资产需要以下步骤：

## 官方流程

### 1. 创建 StaticCategoryFactory

在 `infinigen/assets/static_assets/static_category.py` 中添加：

```python
StaticBedFactory = static_category_factory(
    "infinigen/assets/static_assets/source/Bed",
    z_dim=0.5  # 指定高度为0.5米（可选）
)

StaticChairFactory = static_category_factory(
    "infinigen/assets/static_assets/source/Chair",
    z_dim=1.0  # 指定高度为1.0米
)

StaticCabinetFactory = static_category_factory(
    "infinigen/assets/static_assets/source/Cabinet",
    z_dim=2.0
)
```

### 2. 在 __init__.py 中导入

在 `infinigen/assets/static_assets/__init__.py` 中添加：

```python
from .static_category import (
    StaticBedFactory,
    StaticChairFactory,
    StaticCabinetFactory,
    # ... 其他factory
)
```

### 3. 定义语义

在 `infinigen_examples/constraints/semantics.py` 中添加语义定义。

### 4. 添加约束

在 `infinigen_examples/indoor_constraint_examples.py` 中添加约束。

## 当前问题

我们的 `StaticAssetImporter` 直接使用 `StaticAssetFactory.import_file()` 导入文件，这是**不正确的**。

正确的方式应该是：
1. 使用已定义的 `StaticCategoryFactory`（如 `StaticBedFactory`）
2. 或者先创建对应的 Factory

## 解决方案

### 方案1: 使用现有的 Factory（推荐）

如果 `static_category.py` 中已经定义了对应的 Factory，我们应该使用它们。

### 方案2: 动态创建 Factory

在导入时动态创建 Factory（如果不存在）。

### 方案3: 直接导入文件（当前方式，但需要修复）

直接使用 `StaticAssetFactory.import_file()` 导入，但需要：
- 确保文件格式正确
- 处理尺寸和方向
- 应用材质和标签

## 建议

由于我们的使用场景不同（在已有场景中导入并应用颜色，而不是在场景生成时使用），我们可以：

1. **简化方式**：直接导入文件并应用颜色（当前方式）
2. **完整方式**：创建所有需要的 Factory，然后使用 Factory 导入

让我检查一下现有的 Factory 定义，然后决定最佳方案。
