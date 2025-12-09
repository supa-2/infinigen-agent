# 空资产文件问题修复指南

## 问题描述

所有静态资产文件（GLB格式）都是空文件（大小为0字节），这导致：
- 无法导入资产
- GLB格式验证失败
- 导入时出现 "Bad glTF" 错误

## 原因分析

可能的原因：
1. **占位符文件**：这些文件可能是占位符，需要下载实际的资产文件
2. **下载失败**：文件下载过程中失败，留下了空文件
3. **Git LFS问题**：如果使用Git LFS，可能文件指针没有正确下载
4. **文件损坏**：文件在传输过程中损坏

## 解决方案

### 方案1: 检查是否是Git LFS问题

```bash
cd /home/ubuntu/infinigen
git lfs ls-files | grep "static_assets/source"
git lfs pull  # 如果使用Git LFS，尝试拉取实际文件
```

### 方案2: 重新下载资产文件

根据 Infinigen 官方文档，静态资产需要从外部源下载：

1. **从 Sketchfab 下载**（推荐）：
   - 访问 [Sketchfab](https://sketchfab.com/)
   - 搜索对应的3D模型
   - 下载 GLB 格式文件
   - 放置到对应的文件夹

2. **从 Objaverse 下载**：
   - 使用 Objaverse API 批量下载
   - 参考官方文档中的示例

### 方案3: 使用程序化生成（临时方案）

如果暂时无法获取静态资产文件，可以：
- 使用 `--no-import-assets` 禁用静态资产导入
- 依赖程序化生成器生成家具

```bash
python run_agent.py "生成一个北欧风格的卧室" scene.blend \
    --no-import-assets \
    --render-image
```

### 方案4: 创建占位符资产

如果需要快速测试，可以创建简单的占位符：

```python
import bpy
from infinigen.assets.utils.shapes import create_cube

# 创建简单的占位符
obj = create_cube(size=1.0)
obj.name = "bed_placeholder"
```

## 检查文件状态

运行预处理工具检查：

```bash
cd /home/ubuntu/infinigen/infinigen_agent
python tools/preprocess_static_assets.py
```

## 推荐操作

1. **立即操作**：使用程序化生成作为替代方案
   ```bash
   python run_agent.py "..." scene.blend --no-import-assets
   ```

2. **长期方案**：下载实际的资产文件
   - 参考 `docs/StaticAssets.md` 中的下载链接
   - 或从其他3D模型库下载

3. **验证文件**：下载后运行预处理工具验证

## 文件大小参考

正常的GLB文件大小：
- 简单家具：100KB - 5MB
- 复杂家具：5MB - 50MB
- 如果文件大小为0，说明文件未正确下载

## 注意事项

- 空文件会导致导入失败
- 程序化生成是可靠的替代方案
- 下载资产文件时注意版权许可
