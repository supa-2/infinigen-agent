#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重命名 source 目录下的资产文件，使用统一的命名规范
命名规则：{category}_{name}_{variant}.glb (小写+下划线)
"""
import os
from pathlib import Path

# 源目录
source_dir = Path("/home/ubuntu/infinigen/infinigen/assets/static_assets/source")

# 命名映射：(文件夹, 旧文件名, 新文件名)
rename_list = [
    ("Appliance", "flat_screen_television.glb", "appliance_television_flat_screen.glb"),
    ("Bathtub", "bathtub.glb", "bathtub_standard.glb"),
    ("Bed", "bed1.glb", "bed_standard.glb"),
    ("Cabinet", "file_cabinet.glb", "cabinet_file.glb"),
    ("ceilingHanging", "curtain.glb", "ceiling_hanging_curtain.glb"),
    ("Chair", "chair.glb", "chair_standard.glb"),
    ("Decoration", "plant_interior_decoration.glb", "decoration_plant_interior.glb"),
    ("floorPlant", "palm_plant(1).glb", "floor_plant_palm.glb"),
    ("floorSculpture", "horse_sculpture.glb", "floor_sculpture_horse.glb"),
    ("Lighting", "office_lamp.glb", "lighting_office_lamp.glb"),
    ("Shelf", "metal_shelf_-_14mb.glb", "shelf_metal.glb"),
    ("Sink", "sink.glb", "sink_standard.glb"),
    ("Sofa", "sofa.glb", "sofa_standard.glb"),
    ("Table", "table.glb", "table_standard.glb"),
    ("Toilet", "toilet.glb", "toilet_standard.glb"),
    ("wallArt", "hanging_picture_frame-freepoly.org.glb", "wall_art_picture_frame.glb"),
    ("wallClock", "clock.glb", "wall_clock_standard.glb"),
]

def main():
    print("=" * 70)
    print("重命名 source 目录下的资产文件")
    print("=" * 70)
    print()
    
    if not source_dir.exists():
        print(f"错误：源目录不存在: {source_dir}")
        return
    
    renamed_count = 0
    not_found = []
    
    for folder_name, old_file, new_file in rename_list:
        folder = source_dir / folder_name
        old_path = folder / old_file
        new_path = folder / new_file
        
        if not old_path.exists():
            not_found.append(f"{folder_name}/{old_file}")
            print(f"⚠ 未找到: {folder_name}/{old_file}")
            continue
        
        if new_path.exists():
            print(f"⚠ 目标已存在，跳过: {folder_name}/{new_file}")
            continue
        
        try:
            old_path.rename(new_path)
            print(f"✓ {folder_name}/{old_file}")
            print(f"  -> {folder_name}/{new_file}")
            renamed_count += 1
        except Exception as e:
            print(f"✗ 重命名失败 {folder_name}/{old_file}: {e}")
    
    print()
    print("=" * 70)
    print(f"完成！成功重命名 {renamed_count} 个文件")
    if not_found:
        print(f"\n警告：{len(not_found)} 个文件未找到")
    print("=" * 70)
    
    # 列出重命名后的文件
    print("\n重命名后的文件列表:")
    print("-" * 70)
    for folder in sorted(source_dir.iterdir()):
        if folder.is_dir():
            for file in sorted(folder.glob("*.glb")):
                rel_path = file.relative_to(source_dir)
                print(f"  {rel_path}")
    print("-" * 70)

if __name__ == "__main__":
    main()
