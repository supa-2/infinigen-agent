#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置静态资产 - 删除空文件并提供下载指南
"""
import os
import sys
from pathlib import Path

# 静态资产源目录
SOURCE_DIR = Path("/home/ubuntu/infinigen/infinigen/assets/static_assets/source")

def delete_empty_files():
    """删除所有空文件"""
    print("=" * 70)
    print("步骤1: 删除空文件")
    print("=" * 70)
    
    deleted_count = 0
    deleted_files = []
    
    if not SOURCE_DIR.exists():
        print(f"⚠ 目录不存在: {SOURCE_DIR}")
        return 0
    
    for folder in sorted(SOURCE_DIR.iterdir()):
        if not folder.is_dir():
            continue
        
        for file in folder.iterdir():
            if file.is_file():
                try:
                    size = file.stat().st_size
                    if size == 0:
                        rel_path = file.relative_to(SOURCE_DIR.parent.parent)
                        print(f"  删除: {rel_path}")
                        file.unlink()
                        deleted_count += 1
                        deleted_files.append(str(rel_path))
                except Exception as e:
                    print(f"  ⚠ 无法删除 {file.name}: {e}")
    
    print(f"\n✓ 已删除 {deleted_count} 个空文件")
    return deleted_count

def create_download_instructions():
    """创建下载说明"""
    print("\n" + "=" * 70)
    print("步骤2: 创建下载说明")
    print("=" * 70)
    
    instructions = """# 静态资产下载说明

## 快速开始

由于静态资产文件需要从外部源下载，有以下几种方式：

### 方式1: 使用程序化生成（推荐，立即可用）

如果暂时无法下载资产文件，可以使用程序化生成器：

```bash
cd /home/ubuntu/infinigen/infinigen_agent
conda activate infinigen

python run_agent.py "生成一个北欧风格的卧室" scene.blend \\
    --no-import-assets \\
    --render-image
```

这样会跳过静态资产导入，使用程序化生成器生成所有家具。

### 方式2: 从 Sketchfab 手动下载

1. 访问 https://sketchfab.com/
2. 搜索模型（如 "bed 3d model free"）
3. 筛选：免费 + CC BY 4.0 许可
4. 下载 GLB 格式
5. 放置到对应文件夹

### 方式3: 使用 Objaverse API（批量下载）

```bash
pip install objaverse
```

然后使用 Python API 下载。

## 文件结构

下载后，文件应该放在：

```
infinigen/assets/static_assets/source/
├── Bed/
│   └── bed_standard.glb
├── Chair/
│   └── chair_standard.glb
├── Sofa/
│   └── sofa_standard.glb
├── Table/
│   └── table_standard.glb
└── ...
```

## 验证

下载后运行：

```bash
python tools/preprocess_static_assets.py
```

## 注意事项

- 确保文件大小 > 0（不是空文件）
- 推荐使用 GLB 格式
- 注意版权许可（使用 CC BY 4.0 或类似开放许可）
"""
    
    instructions_path = SOURCE_DIR.parent / "DOWNLOAD_INSTRUCTIONS.md"
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✓ 下载说明已创建: {instructions_path}")
    return instructions_path

def show_current_status():
    """显示当前状态"""
    print("\n" + "=" * 70)
    print("当前状态")
    print("=" * 70)
    
    if not SOURCE_DIR.exists():
        print(f"⚠ 目录不存在: {SOURCE_DIR}")
        return
    
    total_files = 0
    valid_files = 0
    empty_files = 0
    
    for folder in sorted(SOURCE_DIR.iterdir()):
        if not folder.is_dir():
            continue
        
        folder_files = list(folder.glob("*.glb")) + list(folder.glob("*.gltf"))
        if folder_files:
            print(f"\n{folder.name}/")
            for file in sorted(folder_files):
                total_files += 1
                size = file.stat().st_size
                if size == 0:
                    empty_files += 1
                    print(f"  ✗ {file.name}: {size} bytes (空文件)")
                else:
                    valid_files += 1
                    print(f"  ✓ {file.name}: {size:,} bytes")
    
    print(f"\n总计: {total_files} 个文件")
    print(f"  有效: {valid_files}")
    print(f"  空文件: {empty_files}")

def main():
    print("=" * 70)
    print("静态资产设置工具")
    print("=" * 70)
    print()
    
    # 删除空文件
    deleted = delete_empty_files()
    
    # 创建下载说明
    instructions_path = create_download_instructions()
    
    # 显示当前状态
    show_current_status()
    
    print("\n" + "=" * 70)
    print("完成")
    print("=" * 70)
    print()
    print("下一步：")
    print(f"1. 查看下载说明: {instructions_path}")
    print("2. 或使用程序化生成: python run_agent.py ... --no-import-assets")
    print()

if __name__ == "__main__":
    main()
