# 功能更新总结

## 更新内容

已成功实现**优先静态资产，缺失再程序化生成**的新工作流程。

## 新增文件

1. **`src/procedural_furniture_generator.py`**
   - 程序化家具生成器模块
   - 支持多种家具类型的程序化生成
   - 自动映射家具类型到对应的Factory类

## 修改的文件

1. **`src/agent.py`**
   - 更新 `process_request` 方法，实现新的工作流程
   - 添加 `use_procedural_generation` 参数
   - 集成静态资产导入和程序化生成

2. **`run_agent.py`**
   - 添加 `--procedural` 和 `--no-procedural` 命令行选项
   - 支持控制是否使用程序化生成

3. **`docs/NEW_WORKFLOW.md`**
   - 新增工作流程说明文档

## 工作流程

```
用户输入 → 生成色彩方案 → 解析颜色
    ↓
步骤1: 优先从静态资产目录导入家具并应用颜色
    ↓
步骤2: 对缺失的家具，使用程序化生成器生成并应用颜色
    ↓
步骤3: 对不支持程序化生成的家具，在场景中查找已有对象并应用颜色
    ↓
保存最终场景
```

## 支持的家具类型

### 静态资产支持
- Bed, Sofa, Chair, Table, Cabinet, Shelf, 等等

### 程序化生成支持
- bed → `BedFactory`
- sofa/couch → `SofaFactory`
- chair → `ChairFactory`
- table → `TableDiningFactory`
- cabinet → `SingleCabinetFactory`
- bookshelf → `SimpleBookcaseFactory`
- desk → `SimpleDeskFactory`
- 等等...

## 使用示例

```bash
# 基本用法（优先静态资产，缺失再程序化生成）
python run_agent.py "生成一个北欧风的卧室" scene.blend

# 禁用程序化生成
python run_agent.py "生成一个北欧风的卧室" scene.blend --no-procedural

# 禁用静态资产导入
python run_agent.py "生成一个北欧风的卧室" scene.blend --no-import-assets
```

## 优势

1. **质量优先**：静态资产质量更高
2. **灵活补充**：程序化生成补充缺失家具
3. **自动应用颜色**：所有家具自动应用颜色
4. **智能选择**：系统自动判断最佳方式
