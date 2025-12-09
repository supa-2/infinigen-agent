# 改变家具颜色的逻辑说明

## 更新：支持RGB值输入

现在系统已经更新，**优先支持大模型直接输出RGB值**，而不是颜色名称。

---

## 完整流程

### 1. 用户输入 → 大模型生成RGB值

**输入**: "生成一个北欧风的卧室"

**系统提示词**: 引导模型输出RGB格式
```
请按照以下格式输出（使用RGB值，范围0-255）：
1. 床: (255, 255, 255)
2. 床头柜: (210, 180, 140)
3. 沙发: (200, 200, 200)
```

**大模型输出示例**:
```
1. 床: (250, 250, 250)
2. 床头柜: (222, 184, 135)
3. 沙发: (200, 200, 200)
4. 墙壁: (245, 245, 220)
5. 地板: (139, 90, 43)
```

---

### 2. RGB值解析 (`color_parser.py`)

**支持的格式**（按优先级）:

1. **标准RGB格式**: `床: (250, 250, 250)`
2. **RGB()格式**: `床: RGB(255, 255, 255)`
3. **数组格式**: `床: [255, 255, 255]` 或 `床: 255, 255, 255`
4. **JSON格式**: `{"床": [250, 250, 250]}`

**解析逻辑**:
- 使用正则表达式提取 `家具名称: RGB值` 模式
- 验证RGB值范围（0-255）
- 自动将RGB值转换为十六进制
- 尝试从RGB值反推颜色名称（用于显示）

**输出**: `FurnitureColor` 对象列表
```python
FurnitureColor(
    furniture_type="床",
    color_name="北欧白",  # 自动反推
    rgb=(250, 250, 250),
    hex_color="#fafafa"
)
```

---

### 3. 应用到场景 (`scene_color_applier.py`)

#### 3.1 查找场景中的家具对象

**关键词映射**:
```python
"床" → ["bed", "Bed", "BED"]
"沙发" → ["sofa", "Sofa", "SOFA", "couch"]
"椅子" → ["chair", "Chair", "dining_chair"]
```

**查找逻辑**:
- 遍历场景中所有对象 (`bpy.context.scene.objects`)
- 检查对象名称是否包含关键词（不区分大小写）
- 匹配则加入结果列表

#### 3.2 应用颜色到对象

**材质处理流程**:

1. **获取或创建材质**
   ```python
   material = bpy.data.materials.get(material_name)
   if not material:
       material = bpy.data.materials.new(name=material_name)
   ```

2. **重置材质节点**
   - 清除除输出节点外的所有节点
   - 创建新的 `Principled BSDF` 节点

3. **设置RGB颜色**
   ```python
   # RGB值归一化到 0-1 范围
   rgb_normalized = (250/255, 250/255, 250/255, 1.0)
   bsdf.inputs['Base Color'].default_value = rgb_normalized
   ```

4. **连接节点**
   ```
   Principled BSDF → Material Output
   ```

5. **应用到对象**
   - 替换对象的第一个材质槽
   - 或添加新材质

---

## 关键改进

### ✅ 支持RGB值直接输入
- 不再依赖颜色名称映射
- 可以处理任意RGB值
- 自动反推颜色名称用于显示

### ✅ 多种格式支持
- `(R, G, B)` - 标准格式
- `RGB(R, G, B)` - 带RGB前缀
- `[R, G, B]` - 数组格式
- JSON格式

### ✅ 向后兼容
- 仍然支持颜色名称输入
- 如果找不到RGB值，会尝试从颜色名称映射

---

## 使用示例

```python
from src.agent import InfinigenAgent

agent = InfinigenAgent()

# 大模型会自动输出RGB格式
output = agent.process_request(
    user_request="生成一个北欧风的卧室",
    scene_path="scene.blend"
)
```

**大模型输出**:
```
1. 床: (250, 250, 250)
2. 床头柜: (222, 184, 135)
3. 沙发: (200, 200, 200)
```

**系统处理**:
1. 解析RGB值 → `(250, 250, 250)`
2. 查找场景中的"bed"对象
3. 创建/修改材质，设置Base Color为RGB(250, 250, 250)
4. 保存场景

---

## 注意事项

1. **对象查找**: 依赖对象名称包含关键词，如果场景中对象命名不规范，可能找不到
2. **材质覆盖**: 会替换整个材质，只保留Base Color
3. **RGB验证**: 自动验证RGB值范围（0-255），超出范围会被忽略

