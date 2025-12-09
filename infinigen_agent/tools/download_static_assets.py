#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载静态资产文件
根据 Infinigen 官方文档，从 Objaverse 或 Sketchfab 下载资产文件
"""
import os
import sys
import requests
from pathlib import Path
import json

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 静态资产源目录
SOURCE_DIR = Path("/home/ubuntu/infinigen/infinigen/assets/static_assets/source")

# 需要下载的资产列表（可以根据需要修改）
ASSETS_TO_DOWNLOAD = {
    "Bed": {
        "urls": [
            # 可以从 Sketchfab 或其他源获取
            # 示例：需要替换为实际的下载链接
        ],
        "files": ["bed_standard.glb"]
    },
    "Chair": {
        "urls": [],
        "files": ["chair_standard.glb"]
    },
    "Sofa": {
        "urls": [],
        "files": ["sofa_standard.glb"]
    },
    "Table": {
        "urls": [],
        "files": ["table_standard.glb"]
    },
    "Cabinet": {
        "urls": [],
        "files": ["cabinet_file.glb"]
    },
    "Shelf": {
        "urls": [],
        "files": ["shelf_metal.glb"]
    },
}

def download_file(url: str, output_path: Path, chunk_size: int = 8192):
    """下载文件"""
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
        
        print(f"\n✓ 下载完成: {output_path.name} ({downloaded} bytes)")
        return True
    except Exception as e:
        print(f"\n✗ 下载失败: {e}")
        return False

def delete_empty_files():
    """删除所有空文件"""
    print("=" * 70)
    print("删除空文件")
    print("=" * 70)
    
    deleted_count = 0
    for folder in SOURCE_DIR.iterdir():
        if not folder.is_dir():
            continue
        
        for file in folder.iterdir():
            if file.is_file() and file.stat().st_size == 0:
                print(f"删除空文件: {file.relative_to(SOURCE_DIR.parent.parent)}")
                file.unlink()
                deleted_count += 1
    
    print(f"\n✓ 已删除 {deleted_count} 个空文件")
    return deleted_count

def download_from_objaverse_api(uid: str, output_path: Path):
    """使用 Objaverse API 下载资产"""
    try:
        # Objaverse API 端点（需要根据实际API文档调整）
        api_url = f"https://objaverse.allenai.org/api/v1/objects/{uid}/download"
        
        print(f"从 Objaverse 下载: {uid}")
        response = requests.get(api_url, stream=True, timeout=60)
        response.raise_for_status()
        
        # 保存文件
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = output_path.stat().st_size
        print(f"✓ 下载完成: {output_path.name} ({file_size} bytes)")
        return True
    except Exception as e:
        print(f"✗ Objaverse API 下载失败: {e}")
        return False

def create_download_guide():
    """创建下载指南"""
    guide_path = SOURCE_DIR.parent / "DOWNLOAD_GUIDE.md"
    
    guide_content = """# 静态资产下载指南

## 方法1: 从 Sketchfab 手动下载（推荐）

1. 访问 [Sketchfab](https://sketchfab.com/)
2. 搜索对应的3D模型（如 "bed", "chair", "sofa"）
3. 下载 GLB 格式文件
4. 将文件重命名并放置到对应文件夹

### 推荐的免费模型

- **Bed**: 搜索 "bed 3d model free"
- **Chair**: 搜索 "chair 3d model free"  
- **Sofa**: 搜索 "sofa 3d model free"
- **Table**: 搜索 "table 3d model free"

注意：确保模型使用 CC BY 4.0 或类似的开放许可。

## 方法2: 使用 Objaverse API

Objaverse 提供了 Python API 来批量下载资产。

### 安装依赖

```bash
pip install objaverse
```

### 使用示例

```python
from objaverse import Objaverse

objaverse = Objaverse()
# 下载资产
objaverse.download_object(uid="...", save_dir="...")
```

## 方法3: 使用程序化生成（临时方案）

如果暂时无法下载资产，可以使用程序化生成：

```bash
python run_agent.py "..." scene.blend --no-import-assets
```

## 文件放置位置

下载后，将文件放置到：

```
infinigen/assets/static_assets/source/
├── Bed/
│   └── bed_standard.glb
├── Chair/
│   └── chair_standard.glb
├── Sofa/
│   └── sofa_standard.glb
└── ...
```

## 验证文件

运行预处理工具验证：

```bash
python tools/preprocess_static_assets.py
```
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"\n✓ 下载指南已创建: {guide_path}")

def main():
    print("=" * 70)
    print("静态资产下载工具")
    print("=" * 70)
    print()
    
    # 步骤1: 删除空文件
    deleted = delete_empty_files()
    
    print()
    print("=" * 70)
    print("下载选项")
    print("=" * 70)
    print()
    print("由于需要实际的下载链接或API密钥，本脚本提供以下选项：")
    print()
    print("1. 创建下载指南（已创建）")
    print("2. 提供手动下载说明")
    print("3. 使用程序化生成作为替代方案")
    print()
    
    # 创建下载指南
    create_download_guide()
    
    print()
    print("=" * 70)
    print("建议")
    print("=" * 70)
    print()
    print("由于静态资产文件需要从外部源下载，建议：")
    print()
    print("1. 查看下载指南: infinigen/assets/static_assets/DOWNLOAD_GUIDE.md")
    print("2. 从 Sketchfab 手动下载（最简单）")
    print("3. 或使用程序化生成（--no-import-assets）")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
