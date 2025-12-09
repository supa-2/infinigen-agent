#!/usr/bin/env python
"""
Infinigen Agent 运行脚本
使用示例：
    python run_agent.py "生成一个北欧风的卧室" ../outputs/hello_room/coarse/scene.blend
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import InfinigenAgent
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Infinigen 智能体 - 根据自然语言描述生成带颜色的场景"
    )
    parser.add_argument(
        "request",
        type=str,
        help="用户请求，如：'生成一个北欧风的卧室'"
    )
    parser.add_argument(
        "scene_path",
        type=str,
        nargs="?",
        default=None,
        help="输入场景文件路径（.blend 文件）。如果使用 --auto-generate，则不需要此参数"
    )
    parser.add_argument(
        "--auto-generate",
        action="store_true",
        help="自动生成场景（不需要提供 scene_path）"
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default=None,
        help="自动生成场景时的输出文件夹（仅在使用 --auto-generate 时有效）"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="随机种子（仅在使用 --auto-generate 时有效，默认0）"
    )
    parser.add_argument(
        "--infinigen-root",
        type=str,
        default=None,
        help="Infinigen 根目录路径（默认自动检测）"
    )
    parser.add_argument(
        "--generate-timeout",
        type=int,
        default=None,
        help="场景生成超时时间（秒），默认不设置超时"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出场景文件路径（可选，默认在原文件名后加 _colored）"
    )
    parser.add_argument(
        "--render-image",
        action="store_true",
        help="渲染图片"
    )
    parser.add_argument(
        "--render-video",
        action="store_true",
        help="渲染视频"
    )
    parser.add_argument(
        "--video-frames",
        type=int,
        default=60,
        help="视频帧数（默认60）"
    )
    parser.add_argument(
        "--video-fps",
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
        help="渲染分辨率，如 --resolution 1920 1080"
    )
    
    args = parser.parse_args()
    
    # 创建智能体
    agent = InfinigenAgent(infinigen_root=args.infinigen_root)
    
    # 如果使用自动生成场景
    if args.auto_generate:
        if not args.output_folder:
            print("错误: 使用 --auto-generate 时必须指定 --output-folder")
            sys.exit(1)
        
        # 检查场景生成器是否已初始化
        if not agent.scene_generator:
            print("错误: 场景生成器未初始化，无法自动生成场景")
            print("请使用 --infinigen-root 指定 Infinigen 根目录")
            print("例如: --infinigen-root /home/ubuntu/infinigen")
            sys.exit(1)
        
        try:
            resolution = tuple(args.resolution) if args.resolution else None
            
            # 使用完整自动流程
            results = agent.process_request_with_auto_generate(
                user_request=args.request,
                output_folder=args.output_folder,
                seed=args.seed,
                generate_timeout=args.generate_timeout,
                render_image=args.render_image or True,  # 默认渲染图片
                render_video=args.render_video,
                video_frames=args.video_frames,
                video_fps=args.video_fps,
                resolution=resolution
            )
            
            print(f"\n✓ 成功！")
            print(f"生成的场景: {results['generated_scene']}")
            print(f"带颜色的场景: {results['colored_scene']}")
            if 'image' in results:
                print(f"图片: {results['image']}")
            if 'video' in results:
                print(f"视频: {results['video']}")
            
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        return
    
    # 使用已有场景文件
    if not args.scene_path:
        print("错误: 必须提供场景文件路径，或使用 --auto-generate 自动生成")
        sys.exit(1)
    
    # 检查场景文件是否存在
    scene_path = Path(args.scene_path)
    if not scene_path.exists():
        print(f"错误: 场景文件不存在: {scene_path}")
        sys.exit(1)
    
    # 处理请求
    try:
        # 如果指定了渲染选项，使用带渲染的处理方法
        if args.render_image or args.render_video:
            resolution = tuple(args.resolution) if args.resolution else None
            results = agent.process_request_with_render(
                user_request=args.request,
                scene_path=str(scene_path),
                output_path=args.output,
                render_image=args.render_image,
                render_video=args.render_video,
                video_frames=args.video_frames,
                video_fps=args.video_fps,
                resolution=resolution
            )
            print(f"\n✓ 成功！")
            print(f"场景文件: {results['colored_scene']}")
            if 'image' in results:
                print(f"图片: {results['image']}")
            if 'video' in results:
                print(f"视频: {results['video']}")
        else:
            # 只处理颜色，不渲染
            output_path = agent.process_request(
                user_request=args.request,
                scene_path=str(scene_path),
                output_path=args.output
            )
            print(f"\n✓ 成功！输出文件: {output_path}")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

