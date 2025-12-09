#!/usr/bin/env python
"""
渲染视频脚本
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 添加 infinigen 路径
infinigen_root = project_root.parent
sys.path.insert(0, str(infinigen_root))

from src.scene_renderer import SceneRenderer
import argparse


def main():
    parser = argparse.ArgumentParser(description="渲染场景视频")
    parser.add_argument(
        "scene_path",
        type=str,
        help="场景文件路径（.blend 文件）"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出文件夹（默认：场景文件同目录下的 video_output）"
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=60,
        help="视频帧数（默认60）"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="视频帧率（默认24）"
    )
    parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        metavar=("WIDTH", "HEIGHT"),
        default=None,
        help="渲染分辨率，如 --resolution 1280 720"
    )
    
    args = parser.parse_args()
    
    scene_path = Path(args.scene_path)
    if not scene_path.exists():
        print(f"✗ 场景文件不存在: {scene_path}")
        sys.exit(1)
    
    # 确定输出文件夹
    if args.output:
        output_folder = Path(args.output)
    else:
        output_folder = scene_path.parent / "video_output"
    
    resolution = tuple(args.resolution) if args.resolution else None
    
    print("="*60)
    print("开始渲染视频")
    print("="*60)
    print(f"场景文件: {scene_path}")
    print(f"输出文件夹: {output_folder}")
    print(f"帧数: {args.frames}")
    print(f"帧率: {args.fps} fps")
    if resolution:
        print(f"分辨率: {resolution[0]}x{resolution[1]}")
    print("")
    
    try:
        # 创建渲染器
        renderer = SceneRenderer(str(scene_path))
        
        # 渲染视频
        video_path = renderer.render_and_create_video(
            output_folder=str(output_folder),
            num_frames=args.frames,
            fps=args.fps,
            resolution=resolution
        )
        
        print("")
        print("="*60)
        print("✓ 视频渲染完成！")
        print("="*60)
        print(f"视频文件: {video_path}")
        
        # 显示文件信息
        video_file = Path(video_path)
        if video_file.exists():
            size_mb = video_file.stat().st_size / 1024 / 1024
            print(f"文件大小: {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"\n✗ 渲染失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
