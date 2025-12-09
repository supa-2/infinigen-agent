# 资产文件夹映射表

本文档列出了家具类型到实际资产文件夹的映射关系。

## 文件夹结构

实际的资产文件夹位于：`infinigen/assets/static_assets/source/`

## 映射表

| 家具类型（LLM输出） | 文件夹名称 | 说明 |
|-------------------|-----------|------|
| `chair`, `chairs`, `dining_chair` | `Chair/` | 椅子 |
| `table`, `dining_table`, `coffee_table` | `Table/` | 桌子 |
| `sofa`, `couch` | `Sofa/` | 沙发 |
| `bed` | `Bed/` | 床 |
| `cabinet`, `wardrobe`, `closet` | `Cabinet/` | 柜子 |
| `shelf`, `bookshelf`, `bookcase` | `Shelf/` | 书架 |
| `clock`, `wall_clock`, `wallclock` | `wallClock/` | 挂钟 |
| `vase`, `decoration` | `Decoration/` | 装饰品 |
| `sculpture`, `floor_sculpture` | `floorSculpture/` | 地面雕塑 |
| `plant`, `floor_plant` | `floorPlant/` | 地面植物 |
| `wall_art`, `art`, `painting` | `wallArt/` | 墙面艺术 |
| `lamp`, `light`, `lighting` | `Lighting/` | 灯具 |
| `ceiling_light`, `ceiling_hanging`, `chandelier` | `ceilingHanging/` | 吊灯/天花板悬挂物 |
| `toilet` | `Toilet/` | 马桶 |
| `bathtub`, `bath` | `Bathtub/` | 浴缸 |
| `sink` | `Sink/` | 水槽 |
| `appliance`, `tv`, `television`, `refrigerator`, `fridge` | `Appliance/` | 电器 |
| `curtain`, `curtains` | `ceilingHanging/` | 窗帘 |
| `rug`, `carpet` | `Decoration/` | 地毯 |

## 使用示例

当 LLM 输出以下颜色方案时：

```
1. chair: (255, 255, 255)
2. table: (200, 200, 200)
3. clock: (192, 192, 192)
```

Agent 会自动：
1. 查找 `Chair/` 文件夹中的资产
2. 查找 `Table/` 文件夹中的资产
3. 查找 `wallClock/` 文件夹中的资产

## 添加新资产

要添加新的资产类别：

1. 在 `infinigen/assets/static_assets/source/` 下创建新文件夹
2. 将资产文件放入该文件夹
3. 更新 `static_asset_importer.py` 中的 `furniture_folder_map` 字典

例如，要添加 `Nightstand` 类别：

```python
"nightstand": "Nightstand",
"bedside_table": "Nightstand",
```

然后在 `source/` 下创建 `Nightstand/` 文件夹并放入资产文件。

