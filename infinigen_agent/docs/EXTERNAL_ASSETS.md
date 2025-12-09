# 外部资产导入功能

Infinigen Agent 现在支持在已有场景中导入外部资产并应用颜色！

## 功能说明

当场景中缺少某些家具（如椅子、桌子等）时，Agent 可以：
1. 自动从 `infinigen/assets/static_assets/source/` 目录导入对应的外部资产
2. 将颜色应用到导入的资产上

## 使用方法

### 基本用法（自动导入）

```bash
python run_agent.py "生成一个北欧风的卧室" scene.blend
```

默认情况下，Agent 会自动尝试导入缺失的家具资产。

### 禁用自动导入

```bash
python run_agent.py "生成一个北欧风的卧室" scene.blend --no-import-assets
```

### 指定静态资产目录

```bash
python run_agent.py "生成一个北欧风的卧室" scene.blend \
    --static-assets-root /path/to/your/assets
```

## 准备外部资产

### 1. 创建资产文件夹

在 `infinigen/assets/static_assets/source/` 目录下创建家具类别文件夹：

```bash
mkdir -p infinigen/assets/static_assets/source/Chair
mkdir -p infinigen/assets/static_assets/source/Table
mkdir -p infinigen/assets/static_assets/source/Sofa
mkdir -p infinigen/assets/static_assets/source/Bed
# ... 等等
```

### 2. 放置资产文件

将资产文件（支持 .glb, .obj, .fbx, .blend 等格式）放入对应文件夹：

```
infinigen/assets/static_assets/source/
├── Chair/
│   ├── chair1.glb
│   └── chair2.obj
├── Table/
│   └── table.glb
└── Sofa/
    └── sofa.glb
```

### 3. 支持的家具类型

Agent 会自动识别以下家具类型并尝试导入：

- `chair` / `chairs` → `Chair/`
- `table` / `dining_table` / `coffee_table` → `Table/`
- `sofa` / `couch` → `Sofa/`
- `bed` → `Bed/`
- `nightstand` → `Nightstand/`
- `desk` → `Desk/`
- `bookshelf` / `bookcase` → `Bookshelf/`
- `cabinet` → `Cabinet/`
- `wardrobe` → `Wardrobe/`
- `clock` → `Clock/`
- `vase` → `Vase/`
- `lamp` → `Lamp/`
- `curtain` → `Curtain/`
- `rug` → `Rug/`

### 4. 资产文件格式

支持以下格式：
- `.glb` / `.gltf` (推荐)
- `.obj`
- `.fbx`
- `.dae` (Collada)
- `.blend` (Blender)
- `.ply`
- `.stl`
- `.usd`
- `.abc` (Alembic)

## 工作流程

1. **生成颜色方案**：LLM 分析用户请求并生成家具颜色方案
2. **检查缺失资产**：Agent 检查场景中是否存在所需的家具
3. **导入外部资产**：如果缺失，从静态资产目录导入
4. **应用颜色**：将颜色应用到所有家具（包括导入的资产）

## 示例

```bash
# 完整流程：导入资产 + 应用颜色
python run_agent.py "生成一个现代风格的客厅，使用蓝色沙发和白色椅子" \
    scene.blend \
    --import-assets

# 只应用颜色，不导入资产
python run_agent.py "生成一个北欧风的卧室" \
    scene.blend \
    --no-import-assets
```

## 注意事项

1. **资产尺寸**：确保导入的资产尺寸合理（建议在 Blender 中预先调整）
2. **资产方向**：资产的前方应该朝向 +x 方向
3. **文件夹命名**：文件夹名称必须与家具类型映射匹配（见上方列表）
4. **文件格式**：推荐使用 `.glb` 或 `.gltf` 格式，兼容性最好

## 故障排除

### 问题：未找到资产文件夹

**解决方案**：
- 检查文件夹路径是否正确
- 确保文件夹名称与家具类型匹配
- 使用 `--static-assets-root` 指定自定义路径

### 问题：导入的资产尺寸不对

**解决方案**：
- 在 Blender 中打开资产文件
- 调整尺寸到合理范围（通常家具高度在 0.5-2 米）
- 重新保存资产文件

### 问题：导入的资产方向不对

**解决方案**：
- 在 Blender 中旋转资产，使前方朝向 +x 方向
- 重新保存资产文件

