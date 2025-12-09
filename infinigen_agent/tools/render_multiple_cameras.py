#!/usr/bin/env python3
"""
使用多个相机渲染场景图片
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import InfinigenAgent
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="使用多个相机渲染场景图片"
    )
    parser.add_argument(
        "scene_path",
        type=str,
        help="场景文件路径（.blend 文件）"
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default=None,
        help="输出文件夹路径（默认在场景文件同目录下创建 renders 文件夹）"
    )
    parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=(1920, 1080),
        help="渲染分辨率（默认 1920 1080）"
    )
    parser.add_argument(
        "--infinigen-root",
        type=str,
        default=None,
        help="Infinigen 根目录路径（默认自动检测）"
    )
    
    args = parser.parse_args()
    
    # 检查场景文件
    scene_path = Path(args.scene_path)
    if not scene_path.exists():
        print(f"错误: 场景文件不存在: {scene_path}")
        sys.exit(1)
    
    # 设置输出文件夹
    if args.output_folder:
        output_folder = Path(args.output_folder)
    else:
        output_folder = scene_path.parent / "renders"
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # 创建智能体
    agent = InfinigenAgent(infinigen_root=args.infinigen_root)
    
    # 渲染多个相机
    try:
        resolution = tuple(args.resolution)
        rendered_files = agent.render_multiple_cameras(
            scene_path=str(scene_path),
            output_folder=str(output_folder),
            resolution=resolution
        )
        
        print("\n" + "="*60)
        print("✓ 渲染完成！")
        print("="*60)
        print(f"共渲染 {len(rendered_files)} 张图片:")
        for i, file_path in enumerate(rendered_files, 1):
            print(f"  {i}. {file_path}")
        print(f"\n输出文件夹: {output_folder}")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

