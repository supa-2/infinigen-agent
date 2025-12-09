#!/usr/bin/env python3
"""
简单渲染脚本 - 使用多个相机渲染场景
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scene_renderer import SceneRenderer

def main():
    if len(sys.argv) < 2:
        print("用法: python render_simple.py <scene.blend> [output_folder]")
        sys.exit(1)
    
    scene_path = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else str(Path(scene_path).parent / "renders")
    
    print("="*60)
    print("多相机渲染")
    print("="*60)
    print(f"场景文件: {scene_path}")
    print(f"输出文件夹: {output_folder}")
    print()
    
    # 创建渲染器
    renderer = SceneRenderer(scene_path)
    
    # 获取所有相机
    cameras = renderer.get_cameras()
    print(f"找到 {len(cameras)} 个相机:")
    for i, cam in enumerate(cameras, 1):
        print(f"  {i}. {cam.name}")
    
    print("\n开始渲染...")
    
    # 渲染所有相机
    rendered_files = renderer.render_multiple_cameras(
        output_folder=output_folder,
        resolution=(1920, 1080)
    )
    
    print("\n" + "="*60)
    print("✓ 渲染完成！")
    print("="*60)
    print(f"共渲染 {len(rendered_files)} 张图片:")
    for i, file_path in enumerate(rendered_files, 1):
        print(f"  {i}. {file_path}")

if __name__ == "__main__":
    main()

