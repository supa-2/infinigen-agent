# Source 目录资产文件重命名方案

## 命名规范

统一使用格式：`{category}_{name}_{variant}.glb`

- 全部小写字母
- 使用下划线分隔
- 清晰的类别前缀
- 去掉特殊字符和括号

## 重命名列表

| 文件夹 | 旧文件名 | 新文件名 | 说明 |
|--------|---------|---------|------|
| Appliance | `flat_screen_television.glb` | `appliance_television_flat_screen.glb` | 统一类别前缀 |
| Bathtub | `bathtub.glb` | `bathtub_standard.glb` | 添加变体标识 |
| Bed | `bed1.glb` | `bed_standard.glb` | 统一命名格式 |
| Cabinet | `file_cabinet.glb` | `cabinet_file.glb` | 优化顺序 |
| ceilingHanging | `curtain.glb` | `ceiling_hanging_curtain.glb` | 添加类别前缀 |
| Chair | `chair.glb` | `chair_standard.glb` | 添加变体标识 |
| Decoration | `plant_interior_decoration.glb` | `decoration_plant_interior.glb` | 统一类别前缀 |
| floorPlant | `palm_plant(1).glb` | `floor_plant_palm.glb` | 去掉括号，统一格式 |
| floorSculpture | `horse_sculpture.glb` | `floor_sculpture_horse.glb` | 统一类别前缀 |
| Lighting | `office_lamp.glb` | `lighting_office_lamp.glb` | 统一类别前缀 |
| Shelf | `metal_shelf_-_14mb.glb` | `shelf_metal.glb` | 简化，去掉特殊字符 |
| Sink | `sink.glb` | `sink_standard.glb` | 添加变体标识 |
| Sofa | `sofa.glb` | `sofa_standard.glb` | 添加变体标识 |
| Table | `table.glb` | `table_standard.glb` | 添加变体标识 |
| Toilet | `toilet.glb` | `toilet_standard.glb` | 添加变体标识 |
| wallArt | `hanging_picture_frame-freepoly.org.glb` | `wall_art_picture_frame.glb` | 去掉域名，统一格式 |
| wallClock | `clock.glb` | `wall_clock_standard.glb` | 统一类别前缀和变体 |

## 执行方式

### 方式1：使用 Python 脚本（推荐）

```bash
cd /home/ubuntu/infinigen
python3 infinigen_agent/tools/rename_source_assets.py
```

### 方式2：手动重命名

可以使用以下命令逐个重命名：

```bash
cd /home/ubuntu/infinigen/infinigen/assets/static_assets/source

# Appliance
mv Appliance/flat_screen_television.glb Appliance/appliance_television_flat_screen.glb

# Bathtub
mv Bathtub/bathtub.glb Bathtub/bathtub_standard.glb

# Bed
mv Bed/bed1.glb Bed/bed_standard.glb

# Cabinet
mv Cabinet/file_cabinet.glb Cabinet/cabinet_file.glb

# ceilingHanging
mv ceilingHanging/curtain.glb ceilingHanging/ceiling_hanging_curtain.glb

# Chair
mv Chair/chair.glb Chair/chair_standard.glb

# Decoration
mv Decoration/plant_interior_decoration.glb Decoration/decoration_plant_interior.glb

# floorPlant（注意括号需要转义或引号）
mv "floorPlant/palm_plant(1).glb" floorPlant/floor_plant_palm.glb

# floorSculpture
mv floorSculpture/horse_sculpture.glb floorSculpture/floor_sculpture_horse.glb

# Lighting
mv Lighting/office_lamp.glb Lighting/lighting_office_lamp.glb

# Shelf
mv "Shelf/metal_shelf_-_14mb.glb" Shelf/shelf_metal.glb

# Sink
mv Sink/sink.glb Sink/sink_standard.glb

# Sofa
mv Sofa/sofa.glb Sofa/sofa_standard.glb

# Table
mv Table/table.glb Table/table_standard.glb

# Toilet
mv Toilet/toilet.glb Toilet/toilet_standard.glb

# wallArt
mv "wallArt/hanging_picture_frame-freepoly.org.glb" wallArt/wall_art_picture_frame.glb

# wallClock
mv wallClock/clock.glb wallClock/wall_clock_standard.glb
```

## 注意事项

1. **不影响功能**：重命名文件不会影响 `static_asset_importer.py` 的功能，因为代码是按文件夹名称查找资产的，而不是按具体文件名。

2. **备份建议**：在执行重命名前，建议先备份 source 目录：
   ```bash
   cp -r infinigen/assets/static_assets/source infinigen/assets/static_assets/source_backup
   ```

3. **验证**：重命名后，可以运行以下命令验证：
   ```bash
   find infinigen/assets/static_assets/source -name "*.glb" | sort
   ```

## 重命名的好处

1. **统一规范**：所有文件遵循相同的命名规范
2. **易于识别**：文件名清晰地表明类别和内容
3. **便于管理**：去掉特殊字符，便于脚本处理
4. **专业规范**：符合软件项目的文件命名最佳实践
