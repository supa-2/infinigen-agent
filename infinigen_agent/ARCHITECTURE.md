# Infinigen Agent 架构说明

## 整体架构

Infinigen Agent 是一个基于 **LangChain** 的模块化智能体系统，用于根据自然语言描述生成、修改和渲染 3D 场景。

**主要架构：LangChain Agent** (`LangChainInfinigenAgent`)

```
┌─────────────────────────────────────────────────────────────┐
│         LangChainInfinigenAgent (主控制器 - LangChain)      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ GLM4.6 LLM   │  │ Qwen2.5-7B   │  │ SceneGenerator│      │
│  │ (输入验证)   │  │ (颜色生成)   │  │ (场景生成)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ColorParser   │  │SceneColor    │  │SceneRenderer │      │
│  │(颜色解析)    │  │Applier       │  │(渲染图片)    │      │
│  │              │  │(颜色应用)    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌────────────────────────────────────┐   │
│  │RoomType      │  │ ProceduralFurnitureGenerator       │   │
│  │Detector      │  │ (程序化家具生成)                    │   │
│  │(房间识别)    │  └────────────────────────────────────┘   │
│  └──────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. LangChainInfinigenAgent (主控制器) ⭐ 主要架构
**文件**: `src/langchain_agent.py`

**职责**:
- 基于 LangChain 框架构建
- 使用 GLM4.6 验证用户输入
- 使用 Qwen2.5-7B-infinigen 生成颜色方案
- 协调所有子模块，管理完整工作流程

**主要方法**:
- `validate_user_input()` - 使用 GLM4.6 验证用户输入
- `generate_furniture_colors()` - 使用 Qwen 生成颜色方案
- `process_request()` - 完整流程（验证+生成场景+应用颜色+渲染）
- `interactive_mode()` - 交互式模式

**特点**:
- ✅ 基于 LangChain 框架
- ✅ 双模型架构（GLM4.6 验证 + Qwen 生成）
- ✅ 自动房间类型识别
- ✅ 程序化家具生成
- ✅ 官方 hello_room 配置

### 2. GLM4.6 LLM (输入验证)
**集成在**: `LangChainInfinigenAgent`

**职责**:
- 使用 GLM4.6 模型验证用户输入是否合理
- 判断输入是否符合场景生成要求
- 提供改进建议

**特点**:
- 通过 LangChain ChatOpenAI 接口调用
- 温度设置为 0.3（更稳定）

### 3. Qwen2.5-7B-infinigen (颜色生成)
**集成在**: `LangChainInfinigenAgent`

**职责**:
- 使用 Qwen 模型生成家具颜色方案
- 分析用户输入，提取场景类型、风格、家具颜色
- 输出 JSON 格式的颜色方案

**特点**:
- 通过 LangChain ChatOpenAI 接口调用 vLLM API
- 温度设置为 0.7（更有创造性）

### 4. ColorParser (颜色解析器)
**文件**: `src/color_parser.py`

**职责**:
- 从大模型输出中提取家具颜色信息
- 支持多种格式（JSON、自然语言、正则表达式）
- 颜色名称到 RGB 的映射

**主要方法**:
- `parse_colors_from_text()` - 解析颜色文本
- `format_colors_for_display()` - 格式化显示

### 5. SceneGenerator (场景生成器)
**文件**: `src/scene_generator.py`

**职责**:
- 调用 Infinigen 的 `generate_indoors` 命令生成 3D 场景
- 管理场景生成参数（seed、gin 配置等）
- 处理场景生成超时和错误

**主要方法**:
- `generate_scene()` - 生成场景

**特点**:
- 默认使用官方 hello_room 配置（`fast_solve.gin` + `singleroom.gin`）
- 根据用户输入自动识别房间类型
- 自动创建输出目录

### 6. SceneColorApplier (场景颜色应用器)
**文件**: `src/scene_color_applier.py`

**职责**:
- 在 Blender 场景中查找家具对象
- 将颜色应用到对象的材质上
- 保存修改后的场景

**主要方法**:
- `apply_colors_to_scene()` - 应用颜色到场景
- `apply_color_to_object()` - 应用颜色到单个对象
- `find_objects_by_name()` - 根据名称查找对象

### 7. SceneRenderer (场景渲染器)
**文件**: `src/scene_renderer.py`

**职责**:
- 渲染场景图片（PNG）
- 管理渲染参数（分辨率、通道等）

**主要方法**:
- `render_image()` - 渲染单张图片

**特点**:
- 默认只保存最终图像（`save_all_passes=False`）
- 支持保存所有渲染通道（`save_all_passes=True`）
- 自动处理 EXR 到 PNG 转换（如果需要）

### 8. RoomTypeDetector (房间类型检测器)
**文件**: `src/room_type_detector.py`

**职责**:
- 根据用户输入智能识别房间类型
- 支持多种房间类型（Kitchen、Bedroom、LivingRoom 等）

**主要方法**:
- `detect_room_type()` - 检测单个房间类型
- `detect_room_types()` - 检测多个房间类型

**支持的房间类型**:
- Kitchen, Bedroom, LivingRoom, Bathroom, DiningRoom
- Closet, Hallway, Garage, Balcony, Utility
- Office, MeetingRoom, OpenOffice, BreakRoom 等

### 9. ProceduralFurnitureGenerator (程序化家具生成器)
**文件**: `src/procedural_furniture_generator.py`

**职责**:
- 使用 Infinigen 的程序化生成功能生成家具
- 支持多种家具类型（bed、chair、table 等）
- 生成时可直接应用颜色

**主要方法**:
- `generate_furniture()` - 生成家具
- `is_furniture_type_supported()` - 检查是否支持

## 工作流程

### 流程 1: 处理已有场景（应用颜色）

```
用户请求
    ↓
VLLMClient → 生成颜色方案
    ↓
ColorParser → 解析颜色信息
    ↓
SceneColorApplier → 应用颜色到场景
    ↓
输出带颜色的场景文件
```

### 流程 2: 处理已有场景 + 渲染

```
流程 1
    ↓
SceneRenderer → 渲染图片/视频
    ↓
输出场景文件 + 渲染结果
```

### 流程 1: LangChain Agent 完整流程 ⭐ 主要流程

```
用户请求
    ↓
GLM4.6 → 验证用户输入
    ↓
┌─────────────────────────────────────┐
│ 并行执行：                            │
│ 1. Qwen2.5-7B → 生成颜色方案         │
│ 2. RoomTypeDetector → 识别房间类型   │
│    SceneGenerator → 生成场景         │
│    (使用官方 hello_room 配置)        │
└─────────────────────────────────────┘
    ↓
ColorParser → 解析颜色信息
    ↓
┌─────────────────────────────────────┐
│ 步骤1: 程序化生成家具                │
│ ProceduralFurnitureGenerator        │
│ → 生成家具并应用颜色                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 步骤2: 场景中已有对象                │
│ SceneColorApplier → 查找并应用颜色   │
└─────────────────────────────────────┘
    ↓
SceneRenderer → 渲染图片（只保存最终图像）
    ↓
输出完整结果
```

## 数据流

### 颜色数据结构

```python
FurnitureColor:
    - furniture_type: str  # 家具类型（如 "bed", "chair"）
    - color_name: str       # 颜色名称（如 "white", "light gray"）
    - rgb: tuple            # RGB 值 (0-255)
    - hex_color: str        # 十六进制颜色（如 "#FFFFFF"）
```

### 场景文件结构

```
outputs/
└── test_scene/
    ├── scene.blend              # 原始场景
    ├── scene_colored.blend      # 应用颜色后的场景
    ├── rendered_image.png       # 渲染的图片（默认只保存最终图像）
    └── frames/                  # 渲染通道（如果 save_all_passes=True）
        ├── Image/
        ├── Diffuse/
        ├── Glossy/
        └── ...
```

## 配置和参数

### Gin 配置（场景生成）

**默认配置**（匹配官方 hello_room）:
- `fast_solve.gin` - 快速求解（迭代次数: 50/20/3）
- `singleroom.gin` - 单房间限制

**自动覆盖**:
- `compose_indoors.terrain_enabled=False` - 禁用地形
- `restrict_solving.restrict_parent_rooms=["RoomType"]` - 根据用户输入自动识别房间类型

### 渲染配置

**默认行为**:
- `save_all_passes=False` - 只保存最终图像（更快，文件更少）

**可选配置**:
- `save_all_passes=True` - 保存所有渲染通道（14+ 个文件）
- `resolution=(1920, 1080)` - 自定义分辨率

## 模块依赖关系

```
InfinigenAgent
    ├── VLLMClient (独立)
    ├── ColorParser (独立)
    ├── RoomTypeDetector (独立)
    ├── SceneGenerator (依赖 Infinigen)
    ├── SceneColorApplier (依赖 Blender/bpy)
    ├── SceneRenderer (依赖 Blender/bpy)
    └── ProceduralFurnitureGenerator (依赖 Infinigen + Blender/bpy)
```

## 使用示例

### 示例 1: 使用 LangChain Agent（推荐）⭐

```python
from src.langchain_agent import LangChainInfinigenAgent

# 创建 LangChain Agent
agent = LangChainInfinigenAgent()

# 处理完整流程
result = agent.process_request(
    user_input="生成一个北欧风格的卧室，床是白色的，沙发是浅灰色的",
    output_folder="outputs/my_scene",
    seed="42",
    timeout=600
)

if result.get("success"):
    print(f"场景文件: {result['scene_file']}")
    print(f"渲染图片: {result['rendered_image']}")
```

### 示例 2: 交互式模式

```python
from src.langchain_agent import LangChainInfinigenAgent

agent = LangChainInfinigenAgent()
agent.interactive_mode()  # 进入交互式模式
```

### 示例 3: 命令行使用

```bash
cd /home/ubuntu/infinigen/infinigen_agent
python src/langchain_agent.py "生成一个现代风格的客厅"
```

## 扩展性

### 添加新的家具类型

1. 在 `ProceduralFurnitureGenerator` 中添加生成逻辑（添加 Factory 映射）
2. 在 `ColorParser` 中添加颜色映射（如果需要）

### 添加新的渲染通道

1. 在 `SceneRenderer.render_image()` 中添加通道配置
2. 更新 `passes_to_save` 参数

### 添加新的颜色应用方式

1. 在 `SceneColorApplier` 中添加新的材质应用方法
2. 在 `process_request()` 中集成新方法

## 性能优化

### 场景生成速度
- 使用 `fast_solve.gin` 配置（默认）
- 使用 `singleroom.gin` 限制房间数量
- 设置合理的超时时间

### 渲染速度
- 默认只保存最终图像（`save_all_passes=False`）
- 使用较低的分辨率进行测试
- 减少视频帧数（如果渲染视频）

### 颜色应用速度
- 优先使用程序化生成（快速生成家具）
- 场景中已有对象作为备选方案
- ProceduralFurnitureGenerator 支持生成时直接应用颜色，速度较快

## 错误处理

### 常见错误和解决方案

1. **场景生成失败**
   - 检查输出目录是否存在
   - 检查 Infinigen 根目录是否正确
   - 检查 gin 配置是否正确

2. **颜色应用失败**
   - 检查场景中是否存在对应家具
   - 检查颜色解析是否正确
   - 检查 Blender 环境是否正确

3. **渲染失败**
   - 检查场景文件是否存在
   - 检查相机是否存在
   - 检查渲染输出目录权限

## 总结

Infinigen Agent 采用模块化设计，每个组件职责明确，易于维护和扩展。主要特点：

- ✅ **模块化**: 每个组件独立，易于测试和维护
- ✅ **灵活性**: 支持多种使用方式（已有场景、自动生成、渲染等）
- ✅ **可扩展**: 易于添加新功能（新家具类型、新渲染通道等）
- ✅ **性能优化**: 默认使用快速配置，只保存必要文件
- ✅ **智能识别**: 根据用户输入自动识别房间类型
- ✅ **官方兼容**: 使用官方 hello_room 推荐配置

## 主要流程

**LangChain Agent 完整流程**（推荐使用）⭐:
1. 用户输入自然语言描述
2. GLM4.6 验证输入合理性
3. 并行执行：
   - Qwen2.5-7B 生成颜色方案
   - 自动识别房间类型
   - 生成场景（使用官方 hello_room 配置）
4. 解析颜色信息
5. 程序化生成家具并应用颜色
6. 在场景中查找已有对象并应用颜色
7. 渲染图片（只保存最终图像）

**测试方式**:
```bash
cd /home/ubuntu/infinigen
python infinigen_agent/test_user_input.py
```

或者直接使用 LangChain Agent：
```bash
cd /home/ubuntu/infinigen/infinigen_agent
python src/langchain_agent.py "生成一个北欧风格的卧室"
```

