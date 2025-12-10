# 场景生成测试说明

## 快速测试

运行测试脚本：

```bash
cd /home/ubuntu/infinigen
conda activate infinigen
python infinigen_agent/test_scene_generation.py
```

## 测试内容

测试脚本会：

1. **生成场景**
   - 使用 Bedroom 类型（快速）
   - 固定种子（seed=42）以便复现
   - 使用 fast_solve.gin 配置（更快）

2. **渲染场景**
   - 使用新的默认设置：`save_all_passes=True`
   - 直接输出 PNG（不需要转换）
   - 保存所有渲染通道

## 预期输出

```
============================================================
测试场景生成和渲染
============================================================

[1/2] 生成场景...
✓ 场景生成成功: outputs/test_scene_generation/scene.blend

[2/2] 渲染场景（默认 save_all_passes=True，直接输出 PNG）...
✓ 使用相机: ...
✓ 将保存所有渲染通道（共 14 个）
✓ PNG 图片已复制到: ...（无需转换）
✓ 所有渲染通道已保存到: outputs/test_scene_generation/frames
✓ 渲染成功: outputs/test_scene_generation/rendered_image.png
   文件大小: X.XX MB
✓ 所有渲染通道已保存: 14 个通道
   通道列表: Image, AO, DiffCol, DiffDir, DiffInd...

============================================================
✓ 测试完成！
============================================================
场景文件: outputs/test_scene_generation/scene.blend
渲染图片: outputs/test_scene_generation/rendered_image.png
所有通道: outputs/test_scene_generation/frames
============================================================
```

## 输出结构

```
outputs/test_scene_generation/
├── scene.blend              # 场景文件
├── rendered_image.png       # 最终渲染图像（PNG，直接输出）
└── frames/                 # 所有渲染通道
    ├── Image/
    │   └── camera_0/
    │       └── Image_0_0_0001_0.png
    ├── AO/
    ├── DiffCol/
    ├── DiffDir/
    └── ... (其他通道)
```

## 验证要点

1. ✅ **PNG 直接输出**：不需要 EXR 转换
2. ✅ **所有通道保存**：frames 目录包含多个通道
3. ✅ **文件格式正确**：所有文件都是 PNG
4. ✅ **光照正常**：图片看起来自然（因为直接使用 PNG）

## 如果测试失败

1. **场景生成失败**：
   - 检查 Infinigen 环境是否正确
   - 检查是否有足够的磁盘空间
   - 查看错误日志

2. **渲染失败**：
   - 检查 Blender 是否正确安装
   - 检查场景文件是否存在
   - 检查是否有相机

3. **找不到 PNG**：
   - 检查 frames/Image/camera_0/ 目录
   - 可能需要等待渲染完成

## 手动测试

如果想手动测试：

```python
from infinigen_agent.src.scene_generator import SceneGenerator
from infinigen_agent.src.scene_renderer import SceneRenderer

# 生成场景
generator = SceneGenerator()
scene_path = generator.generate_scene(
    output_folder="outputs/my_test",
    seed=42,
    task="coarse",
    gin_configs=["fast_solve.gin", "singleroom.gin"],
    gin_overrides=[
        "compose_indoors.terrain_enabled=False",
        "restrict_solving.restrict_parent_rooms=[\"Bedroom\"]"
    ]
)

# 渲染（默认 save_all_passes=True）
renderer = SceneRenderer(str(scene_path))
png_path = renderer.render_image("outputs/my_test/rendered.png")
print(f"完成！图片: {png_path}")
```

