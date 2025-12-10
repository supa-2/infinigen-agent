# 多图片输出解决方案

## 问题

官方命令生成的场景有很多图片（多个渲染通道），但使用 agent 后只有一张图片。

## 原因

- **官方命令**：使用 `passes_to_save` 配置保存了多个渲染通道（passes）
- **Agent 默认**：只保存最终合成图像（Image 通道）

## 解决方案

### ✅ 方法 1：保存所有通道（推荐）

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("scene.blend")
# 设置 save_all_passes=True 保存所有通道
png_path = renderer.render_image(
    "output.png",
    save_all_passes=True  # 关键参数！
)
```

**结果：**
- 主输出：`output.png`（最终合成图像）
- 所有通道：`output.png` 所在目录的 `frames/` 子目录

### 方法 2：选择特定通道

```python
renderer = SceneRenderer("scene.blend")
png_path = renderer.render_image(
    "output.png",
    passes_to_save=[
        "Image",      # 最终图像
        "AO",         # 环境光遮蔽
        "DiffCol",    # 漫反射颜色
    ]
)
```

## 渲染通道说明

官方命令会保存以下通道：

1. **Image** - 最终合成图像（RGB）⭐
2. **DiffDir** - 直接漫反射
3. **DiffCol** - 漫反射颜色
4. **DiffInd** - 间接漫反射
5. **GlossDir** - 直接光泽
6. **GlossCol** - 光泽颜色
7. **GlossInd** - 间接光泽
8. **TransDir** - 直接透射
9. **TransCol** - 透射颜色
10. **TransInd** - 间接透射
11. **VolumeDir** - 体积直接光照
12. **Emit** - 发射光
13. **Env** - 环境光
14. **AO** - 环境光遮蔽

## 输出结构

使用 `save_all_passes=True` 后，输出目录结构：

```
outputs/
  └── your_output/
      ├── output.png          # 最终合成图像
      └── frames/             # 所有渲染通道
          ├── Image/
          │   └── camera_0/
          │       ├── Image_0_0_0001_0.png
          │       └── Image_0_0_0001_0.exr
          ├── AO/
          │   └── camera_0/
          │       └── AO_0_0_0001_0.png
          ├── DiffCol/
          │   └── camera_0/
          │       └── DiffCol_0_0_0001_0.png
          ├── DiffDir/
          ├── GlossCol/
          └── ... (其他通道)
```

## 完整示例

```python
from infinigen_agent.src.scene_renderer import SceneRenderer

# 加载场景
renderer = SceneRenderer("outputs/hello_room/coarse/scene.blend")

# 渲染并保存所有通道
png_path = renderer.render_image(
    "outputs/my_render/rendered_image.png",
    save_all_passes=True  # 保存所有通道
)

print(f"主图像: {png_path}")
print(f"所有通道: outputs/my_render/frames/")
```

## 对比

| 方式 | 输出文件数 | 用途 |
|------|-----------|------|
| 默认（只 Image） | 1 个 | 快速预览 |
| `save_all_passes=True` | 15+ 个 | 完整渲染数据，像官方命令 |
| 自定义通道 | 指定数量 | 特定需求 |

## 注意事项

1. **文件大小**：保存所有通道会生成很多文件，占用更多空间
2. **渲染时间**：保存更多通道不会显著增加渲染时间（通道是同时计算的）
3. **EXR vs PNG**：某些通道可能保存为 EXR 格式，需要转换

## 为什么需要多个通道？

这些通道可以用于：
- **后期合成**：在外部软件中重新组合光照
- **光照分析**：研究不同光照组件
- **材质编辑**：单独调整材质属性
- **研究渲染过程**：理解渲染管线

## 快速测试

```bash
# 在 Python 中测试
python3 << EOF
from infinigen_agent.src.scene_renderer import SceneRenderer

renderer = SceneRenderer("outputs/hello_room/coarse/scene.blend")
png_path = renderer.render_image(
    "outputs/test_all_passes/rendered.png",
    save_all_passes=True
)
print(f"完成！主图像: {png_path}")
print(f"所有通道: outputs/test_all_passes/frames/")
EOF
```

