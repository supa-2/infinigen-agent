# 程序化下载静态资产

## 使用 Objaverse API

可以使用 Objaverse Python API 程序化下载3D模型。

### 安装

```bash
pip install objaverse
```

### 使用方法

```bash
cd /home/ubuntu/infinigen/infinigen_agent
python tools/download_from_objaverse.py
```

### 手动使用 API

```python
import objaverse.xl as oxl

# 获取所有注释
annotations = oxl.get_annotations()

# 筛选家具类别
beds = annotations[annotations['category'].str.contains('bed', case=False, na=False)]

# 下载
oxl.download_objects(beds.head(1), save_dir="path/to/save")
```

## 在生成时直接指定颜色

现在程序化生成器支持在生成时直接指定颜色！

### 使用方式

```python
from src.procedural_furniture_generator import ProceduralFurnitureGenerator

generator = ProceduralFurnitureGenerator(factory_seed=123)

# 生成时直接指定RGB颜色
bed = generator.generate_furniture(
    furniture_type="bed",
    location=(0, 0, 0),
    color=(250, 250, 250)  # 白色 RGB
)
```

### 在 Agent 中使用

Agent 现在会在生成家具时自动应用颜色：

```python
# 自动在生成时应用颜色
obj = generator.generate_furniture(
    furniture_type="bed",
    color=color.rgb  # 从大模型获取的RGB值
)
```

## 优势

1. **程序化下载**：可以使用 Objaverse API 批量下载
2. **生成时着色**：不需要先生成再应用颜色，一步完成
3. **更高效**：减少材质创建和应用的步骤

## 注意事项

- Objaverse API 可能需要网络连接
- 下载的模型需要符合版权要求
- 生成时着色会覆盖原有的程序化材质
