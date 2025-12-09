#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Objaverse API 程序化下载静态资产
"""
import os
import sys
from pathlib import Path
import pandas as pd

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 静态资产源目录
SOURCE_DIR = Path("/home/ubuntu/infinigen/infinigen/assets/static_assets/source")

# 家具类别到搜索关键词的映射
FURNITURE_KEYWORDS = {
    "Bed": ["bed", "mattress", "bedroom"],
    "Chair": ["chair", "seat", "dining chair"],
    "Sofa": ["sofa", "couch", "settee"],
    "Table": ["table", "dining table", "coffee table"],
    "Cabinet": ["cabinet", "wardrobe", "closet"],
    "Shelf": ["shelf", "bookshelf", "bookcase"],
    "Desk": ["desk", "office desk", "writing desk"],
}

def check_objaverse_installed():
    """检查是否安装了objaverse"""
    try:
        import objaverse
        return True
    except ImportError:
        return False

def install_objaverse():
    """安装objaverse"""
    print("正在安装 objaverse...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "objaverse"])
        print("✓ objaverse 安装成功")
        return True
    except Exception as e:
        print(f"✗ 安装失败: {e}")
        return False

def download_from_objaverse(category: str, output_dir: Path, max_objects: int = 1):
    """
    从 Objaverse 下载资产
    
    Args:
        category: 家具类别（如 "Bed", "Chair"）
        output_dir: 输出目录
        max_objects: 最大下载数量
    """
    try:
        import objaverse.xl as oxl
        
        print(f"\n正在从 Objaverse 搜索 {category}...")
        
        # 获取所有注释
        print("  获取对象注释...")
        annotations = oxl.get_annotations()
        
        # 根据关键词搜索
        keywords = FURNITURE_KEYWORDS.get(category, [category.lower()])
        print(f"  搜索关键词: {keywords}")
        
        # 筛选符合条件的对象
        # 注意：这里需要根据实际的annotations结构来筛选
        # 示例：根据category或metadata筛选
        filtered = annotations[
            annotations['category'].str.contains('|'.join(keywords), case=False, na=False)
        ]
        
        if len(filtered) == 0:
            print(f"  ⚠ 未找到匹配的对象")
            return False
        
        # 选择前几个对象
        selected = filtered.head(max_objects)
        
        print(f"  找到 {len(selected)} 个匹配对象，下载前 {max_objects} 个...")
        
        # 下载对象
        downloaded = oxl.download_objects(selected, save_dir=str(output_dir))
        
        if downloaded:
            print(f"  ✓ 成功下载到: {output_dir}")
            return True
        else:
            print(f"  ✗ 下载失败")
            return False
            
    except Exception as e:
        print(f"  ✗ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("使用 Objaverse API 下载静态资产")
    print("=" * 70)
    print()
    
    # 检查是否安装
    if not check_objaverse_installed():
        print("⚠ objaverse 未安装")
        response = input("是否安装 objaverse? (y/n): ")
        if response.lower() == 'y':
            if not install_objaverse():
                print("\n请手动安装: pip install objaverse")
                return
        else:
            print("\n请先安装: pip install objaverse")
            return
    
    # 确保输出目录存在
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 要下载的类别
    categories_to_download = ["Bed", "Chair", "Sofa", "Table"]
    
    print(f"\n将下载以下类别: {', '.join(categories_to_download)}")
    print("每个类别下载 1 个模型")
    print()
    
    success_count = 0
    for category in categories_to_download:
        category_dir = SOURCE_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"下载 {category}")
        print(f"{'='*70}")
        
        if download_from_objaverse(category, category_dir, max_objects=1):
            success_count += 1
    
    print("\n" + "=" * 70)
    print("下载完成")
    print("=" * 70)
    print(f"成功下载: {success_count}/{len(categories_to_download)} 个类别")
    print()
    print("验证文件:")
    print("  python tools/preprocess_static_assets.py")

if __name__ == "__main__":
    main()
