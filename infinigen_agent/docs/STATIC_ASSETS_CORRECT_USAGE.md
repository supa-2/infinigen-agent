# 静态资产正确使用方法

## 问题

根据 Infinigen 官方文档（`docs/StaticAssets.md`），导入外部静态资产需要：

1. **创建 StaticCategoryFactory**：在 `static_category.py` 中使用 `static_category_factory()` 创建
2. **注册 Factory**：在 `__init__.py` 中导入
3. **定义语义**：在 `semantics.py` 中定义
4. **添加约束**：在 `indoor_constraint_examples.py` 中添加约束

## 我们之前的错误

我们直接使用 `StaticAssetFactory.import_file()` 导入文件，这是**不正确的**。

正确的方式应该使用 `StaticCategoryFactory` 的 `create_asset()` 方法。

## 修复方案

### 方案1: 使用现有的 Factory（如果已定义）

如果 `static_category.py` 中已经定义了对应的 Factory（如 `StaticBedFactory`），直接使用：

```python
from infinigen.assets.static_assets import StaticBedFactory

factory = StaticBedFactory(factory_seed=123, coarse=False)
obj = factory.create_asset()
```

### 方案2: 动态创建 Factory（推荐）

对于未定义的类别，动态创建 Factory：

```python
from infinigen.assets.static_assets.static_category import static_category_factory

# 动态创建 Factory
factory_class = static_category_factory("path/to/assets")
factory = factory_class(factory_seed=123, coarse=False)
obj = factory.create_asset()
```

### 方案3: 直接导入（回退方案）

如果 Factory 方式失败，回退到直接导入：

```python
from infinigen.assets.static_assets.base import StaticAssetFactory

factory = StaticAssetFactory(factory_seed=0)
obj = factory.import_file("path/to/file.glb")
```

## 当前实现

我已经修改了 `StaticAssetImporter`，现在会：

1. **优先使用 Factory 方式**：动态创建 `StaticCategoryFactory` 并使用 `create_asset()`
2. **自动回退**：如果 Factory 方式失败，回退到直接导入方式
3. **保持兼容**：不影响现有功能

## 注意事项

### Factory 方式的优势

- ✅ 自动处理尺寸缩放（如果指定了 `z_dim` 等）
- ✅ 自动处理方向（如果指定了 `rotation_euler`）
- ✅ 自动标记支持表面（如果 `tag_support=True`）
- ✅ 符合官方文档规范

### 直接导入方式的限制

- ❌ 需要手动处理尺寸
- ❌ 需要手动处理方向
- ❌ 需要手动标记表面
- ❌ 不符合官方文档规范

## 使用建议

1. **优先使用 Factory 方式**（已实现）
2. **如果文件损坏导致导入失败**，检查文件格式
3. **如果需要自定义尺寸/方向**，在 `static_category.py` 中创建 Factory 时指定参数

## 示例

```python
# 使用 Factory 方式（推荐）
factory_class = static_category_factory(
    "infinigen/assets/static_assets/source/Bed",
    z_dim=0.5  # 指定高度为0.5米
)
factory = factory_class(factory_seed=123, coarse=False)
bed_obj = factory.create_asset()
```
