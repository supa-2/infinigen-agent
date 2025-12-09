# Seed 和相机选择说明

## Seed 设置

### 随机 Seed

现在支持自动随机生成 seed：

1. **命令行参数**：`--seed` 默认为 `None`，表示随机生成
   ```bash
   # 随机seed
   python run_agent.py "生成一个北欧风的卧室" --auto-generate --output-folder outputs/test
   
   # 指定seed
   python run_agent.py "生成一个北欧风的卧室" --auto-generate --output-folder outputs/test --seed 12345
   ```

2. **代码中**：`generate_scene_from_request()` 和 `generate_scene()` 的 `seed` 参数默认为 `None`
   - 如果为 `None`，会自动生成 1 到 1e9 之间的随机整数

### 为什么使用随机 Seed？

- 每次生成不同的场景布局
- 避免重复的场景结构
- 增加场景多样性

## 相机选择

### 问题

之前生成的图片可能显示建筑外部，而不是室内场景。这是因为：

1. 场景中可能有多个相机（室内相机、外部相机、俯视相机等）
2. 之前的代码简单地选择第一个相机，可能不是室内相机

### 解决方案

现在改进了相机选择逻辑：

1. **优先选择相机rig的子相机**
   - Infinigen 的 `generate_indoors` 会创建相机rig（camera rigs）
   - 相机rig的子相机通常是室内相机，用于渲染室内场景
   - 这些相机通过 `camera_rigs[0].children[0]` 访问

2. **选择顺序**：
   ```
   1. 相机rig的子相机（优先，通常是室内相机）
   2. 直接相机对象
   3. 场景默认相机
   4. 创建新相机（如果都没有）
   ```

### 代码实现

在 `scene_renderer.py` 中：

```python
def get_cameras(self):
    """获取场景中的所有相机，优先返回相机rig的子相机（室内相机）"""
    camera_rig_children = []  # 相机rig的子相机（通常是室内相机）
    direct_cameras = []  # 直接相机对象
    
    # 查找相机rig的子相机
    for obj in bpy.context.scene.objects:
        if 'camera' in obj.name.lower() or 'cam' in obj.name.lower():
            for child in obj.children:
                if child.type == 'CAMERA':
                    camera_rig_children.append(child)
    
    # 优先使用相机rig的子相机
    if camera_rig_children:
        cameras.extend(camera_rig_children)
    
    # 然后添加直接相机对象
    if direct_cameras:
        cameras.extend(direct_cameras)
    
    return cameras
```

### 验证

渲染时会显示使用的相机信息：

```
✓ 找到 1 个相机rig子相机（室内相机）
✓ 使用相机: Camera (位置: (2.5, -3.0, 1.2))
```

## 相关文件

- `src/scene_renderer.py`: 相机选择逻辑
- `src/scene_generator.py`: Seed 处理
- `src/agent.py`: Seed 处理
- `run_agent.py`: 命令行参数

