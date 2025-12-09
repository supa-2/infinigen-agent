# 问题修复说明

## 已修复的问题

### 1. 静态资产导入失败（GLB文件格式错误）

**问题**：
```
Error: Bad glTF: json error: Expecting value: line 1 column 1 (char 0)
```

**原因**：
- GLB文件可能损坏或格式不正确
- 文件可能为空或不是有效的GLB格式

**修复**：
- 添加了文件存在性检查
- 添加了文件大小检查（空文件检测）
- 添加了GLB/GLTF文件格式验证
- 改进了错误处理和日志输出

**位置**：`src/static_asset_importer.py`

### 2. 程序化生成失败（SofaFactory不支持coarse参数）

**问题**：
```
TypeError: SofaFactory.__init__() got an unexpected keyword argument 'coarse'
```

**原因**：
- 某些Factory类（如SofaFactory）不支持`coarse`参数
- 代码假设所有Factory都支持`coarse`参数

**修复**：
- 使用`inspect.signature`检查Factory是否支持`coarse`参数
- 如果支持，传递`coarse`参数；如果不支持，只传递`factory_seed`

**位置**：`src/procedural_furniture_generator.py`

### 3. 渲染失败（passes_to_save格式错误）

**问题**：
```
ValueError: too many values to unpack (expected 2)
```

**原因**：
- Infinigen的`render_image`函数期望`passes_to_save`是元组列表：`[(viewlayer_pass, socket_name), ...]`
- 代码传递的是字符串列表：`["Image"]`

**修复**：
- 自动检测格式并转换
- 如果是字符串列表，转换为元组列表：`[("Image", "Image")]`
- 如果已经是元组列表，直接使用

**位置**：`src/scene_renderer.py`

## 测试建议

### 测试静态资产导入

如果静态资产文件有问题，可以：

1. **检查文件**：
   ```bash
   file /home/ubuntu/infinigen/infinigen/assets/static_assets/source/Bed/bed_standard.glb
   ls -lh /home/ubuntu/infinigen/infinigen/assets/static_assets/source/Bed/
   ```

2. **如果文件损坏，可以跳过静态资产导入**：
   ```bash
   python run_agent.py "..." scene.blend --no-import-assets
   ```

3. **或者使用程序化生成**（会自动处理缺失的家具）

### 测试程序化生成

现在所有支持的Factory都会正确初始化，包括：
- ✅ BedFactory（支持coarse）
- ✅ SofaFactory（不支持coarse，已修复）
- ✅ ChairFactory（支持coarse）
- ✅ TableFactory（支持coarse）

### 测试渲染

渲染现在应该可以正常工作：

```bash
python run_agent.py "..." scene.blend --render-image --resolution 1280 720
```

## 已知限制

1. **静态资产文件**：如果GLB文件损坏，需要重新下载或使用程序化生成
2. **渲染通道**：目前只支持基本的Image通道，其他通道（如Depth）需要正确配置
3. **程序化生成位置**：生成的家具默认在原点，可能需要手动调整位置

## 下一步

1. 检查并修复损坏的静态资产文件
2. 测试完整的流程
3. 根据需要调整家具位置
