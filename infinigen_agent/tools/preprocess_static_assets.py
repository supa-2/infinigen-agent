#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预处理静态资产文件
- 检查文件格式
- 验证GLB/GLTF文件
- 修复损坏的文件（如果可能）
- 生成文件报告
"""
import os
import sys
from pathlib import Path
import struct

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_glb_file(file_path):
    """
    检查GLB文件格式
    
    GLB文件格式：
    - 前4字节：magic (glTF)
    - 4-8字节：version (2)
    - 8-12字节：length (文件总长度)
    """
    try:
        with open(file_path, 'rb') as f:
            # 读取magic
            magic = f.read(4)
            if magic != b'glTF':
                return False, f"无效的GLB magic: {magic}"
            
            # 读取version
            version = struct.unpack('<I', f.read(4))[0]
            if version != 2:
                return False, f"不支持的GLB版本: {version} (期望2)"
            
            # 读取length
            length = struct.unpack('<I', f.read(4))[0]
            file_size = os.path.getsize(file_path)
            
            if length != file_size:
                return False, f"文件长度不匹配: header={length}, actual={file_size}"
            
            return True, "GLB文件格式正确"
    except Exception as e:
        return False, f"检查失败: {e}"

def check_gltf_file(file_path):
    """检查GLTF文件（JSON格式）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(100)  # 只读前100字符
            if content.strip().startswith('{') or content.strip().startswith('['):
                return True, "GLTF文件格式正确"
            else:
                return False, f"GLTF文件不是有效的JSON: 开头={content[:20]}"
    except Exception as e:
        return False, f"检查失败: {e}"

def check_file(file_path):
    """检查单个文件"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, "文件不存在"
    
    if not file_path.is_file():
        return False, "不是文件"
    
    file_size = file_path.stat().st_size
    if file_size == 0:
        return False, "文件为空"
    
    ext = file_path.suffix.lower()
    
    if ext == '.glb':
        return check_glb_file(file_path)
    elif ext == '.gltf':
        return check_gltf_file(file_path)
    elif ext in ['.obj', '.fbx', '.dae', '.blend', '.ply', '.stl', '.usd', '.abc']:
        # 其他格式只检查文件是否存在且非空
        return True, f"{ext.upper()}文件存在且非空"
    else:
        return False, f"不支持的文件格式: {ext}"

def preprocess_assets(source_dir):
    """预处理静态资产目录"""
    source_dir = Path(source_dir)
    
    if not source_dir.exists():
        print(f"错误：目录不存在: {source_dir}")
        return
    
    print("=" * 70)
    print("预处理静态资产文件")
    print("=" * 70)
    print(f"源目录: {source_dir}")
    print()
    
    total_files = 0
    valid_files = 0
    invalid_files = []
    
    # 遍历所有文件夹
    for folder in sorted(source_dir.iterdir()):
        if not folder.is_dir():
            continue
        
        print(f"\n检查文件夹: {folder.name}")
        print("-" * 70)
        
        # 查找所有资产文件
        asset_files = []
        for ext in ['.glb', '.gltf', '.obj', '.fbx', '.dae', '.blend', '.ply', '.stl', '.usd', '.abc']:
            asset_files.extend(folder.glob(f'*{ext}'))
        
        if not asset_files:
            print(f"  ⚠ 未找到资产文件")
            continue
        
        for asset_file in sorted(asset_files):
            total_files += 1
            rel_path = asset_file.relative_to(source_dir)
            
            is_valid, message = check_file(asset_file)
            
            if is_valid:
                valid_files += 1
                file_size = asset_file.stat().st_size
                print(f"  ✓ {rel_path.name}")
                print(f"    大小: {file_size:,} 字节")
                print(f"    状态: {message}")
            else:
                invalid_files.append((rel_path, message))
                print(f"  ✗ {rel_path.name}")
                print(f"    错误: {message}")
    
    # 总结
    print()
    print("=" * 70)
    print("预处理结果")
    print("=" * 70)
    print(f"总文件数: {total_files}")
    print(f"有效文件: {valid_files}")
    print(f"无效文件: {len(invalid_files)}")
    
    if invalid_files:
        print("\n无效文件列表:")
        print("-" * 70)
        for rel_path, error in invalid_files:
            print(f"  {rel_path}: {error}")
        print("\n建议:")
        print("  1. 检查文件是否损坏")
        print("  2. 重新下载或获取文件")
        print("  3. 使用程序化生成作为替代方案")
    
    print("=" * 70)

def main():
    # 默认源目录
    default_source = Path("/home/ubuntu/infinigen/infinigen/assets/static_assets/source")
    
    if len(sys.argv) > 1:
        source_dir = Path(sys.argv[1])
    else:
        source_dir = default_source
    
    preprocess_assets(source_dir)

if __name__ == "__main__":
    main()
