# Infinigen 家具存储位置

## 主要存储目录

家具资产存储在 `infinigen/assets/objects/` 目录下，按类型分类：

### 室内家具

#### 1. 座椅类 (`seating/`)
- **床**: `seating/bed.py` - `BedFactory`
- **床架**: `seating/bedframe.py` - `BedFrameFactory`
- **床垫**: `seating/mattress.py` - `MattressFactory`
- **沙发**: `seating/sofa.py` - `SofaFactory`, `ArmChairFactory`
- **椅子**: `seating/chairs/chair.py` - `ChairFactory`
- **办公椅**: `seating/chairs/office_chair.py` - `OfficeChairFactory`
- **吧台椅**: `seating/chairs/bar_chair.py` - `BarChairFactory`
- **枕头**: `seating/pillow.py` - `PillowFactory`

#### 2. 桌子类 (`tables/`)
- **餐桌**: `tables/dining_table.py` - `TableDiningFactory`
- **边桌**: `tables/dining_table.py` - `SideTableFactory`
- **咖啡桌**: `tables/dining_table.py` - `CoffeeTableFactory`
- **鸡尾酒桌**: `tables/cocktail_table.py` - `TableCocktailFactory`
- **桌面**: `tables/table_top.py` - `TableTopFactory`
- **桌腿**: `tables/legs/`

#### 3. 架子类 (`shelves/`)
- **书架/书柜**: `shelves/` 目录下的各种 Factory

#### 4. 灯具类 (`lamp/`)
- **台灯**: `lamp/lamp.py` - `DeskLampFactory`
- **落地灯**: `lamp/lamp.py` - `FloorLampFactory`
- **吊灯**: `lamp/ceiling_lights.py` - `CeilingLightFactory`
- **经典吊灯**: `lamp/ceiling_classic_lamp.py` - `CeilingClassicLampFactory`

#### 5. 家电类 (`appliances/`)
- **洗碗机**: `appliances/dishwasher.py` - `DishwasherFactory`
- **微波炉**: `appliances/microwave.py` - `MicrowaveFactory`
- 其他家电...

#### 6. 浴室用品 (`bathroom/`)
- **浴缸**: `bathroom/` - `BathtubFactory`
- **洗手池**: `bathroom/bathroom_sink.py` - `BathroomSinkFactory`, `StandingSinkFactory`

#### 7. 墙面装饰 (`wall_decorations/`)
- **墙面艺术**: `wall_decorations/wall_art.py` - `WallArtFactory`
- **镜子**: `wall_decorations/wall_art.py` - `MirrorFactory`
- **墙面架**: `wall_decorations/wall_shelf.py` - `WallShelfFactory`
- **抽油烟机**: `wall_decorations/range_hood.py` - `RangeHoodFactory`
- **气球**: `wall_decorations/balloon.py` - `BalloonFactory`

#### 8. 窗户 (`windows/`)
- **窗户**: `windows/window.py` - `WindowFactory`

#### 9. 装饰品 (`table_decorations/`)
- **书**: `table_decorations/book.py` - `BookFactory`, `BookColumnFactory`, `BookStackFactory`
- **花瓶**: `table_decorations/vase.py` - `VaseFactory`
- **水槽**: `table_decorations/sink.py` - `SinkFactory`, `TapFactory`

#### 10. 组织/储物 (`organizer/`)
- 各种储物和组织相关的家具

## 在代码中查找家具对象

### 方法1: 通过 Factory 类名查找

```python
# 例如查找床
from infinigen.assets.objects.seating.bed import BedFactory

# 查找沙发
from infinigen.assets.objects.seating.sofa import SofaFactory

# 查找椅子
from infinigen.assets.objects.seating.chairs.chair import ChairFactory
```

### 方法2: 在 Blender 场景中查找

家具在场景中的命名通常包含 Factory 类名，例如：
- `BedFactory` 生成的对象可能命名为 `bed_xxx` 或 `Bed_xxx`
- `SofaFactory` 生成的对象可能命名为 `sofa_xxx` 或 `Sofa_xxx`

### 方法3: 通过对象类型标签查找

Infinigen 使用标签系统来标记对象类型，可以通过标签查找：
- `Subpart.Bed`
- `Subpart.Sofa`
- `Subpart.Chair`
- 等等

## 在智能体中使用

在 `scene_color_applier.py` 中，我们已经实现了通过关键词查找对象的功能：

```python
keyword_map = {
    "床": ["bed", "Bed", "BED"],
    "沙发": ["sofa", "Sofa", "SOFA", "couch"],
    "椅子": ["chair", "Chair", "dining_chair"],
    # ...
}
```

这些关键词对应到场景中的对象名称，可以用于查找和修改颜色。

## 相关文件

- 家具定义: `infinigen/assets/objects/`
- 材质定义: `infinigen/assets/materials/`
- 颜色定义: `infinigen/assets/colors.py`
- 场景组合: `infinigen/core/placement/`

