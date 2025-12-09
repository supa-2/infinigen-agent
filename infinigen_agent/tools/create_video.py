#!/usr/bin/env python
"""
将渲染的图片转换为视频
"""
import subprocess
import sys
from pathlib import Path

def create_video_from_image(image_path, output_path, duration=5, fps=24):
    """将单帧图片转换为视频"""
    image_path = Path(image_path)
    output_path = Path(output_path)
    
    if not image_path.exists():
        print(f"✗ 图片文件不存在: {image_path}")
        return False
    
    print(f"正在生成视频...")
    print(f"图片: {image_path}")
    print(f"输出: {output_path}")
    print(f"时长: {duration}秒")
    print(f"帧率: {fps} fps")
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 使用 ffmpeg 生成视频
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-t", str(duration),
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        "-vcodec", "libx264",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"\n✓ 视频生成成功: {output_path}")
        
        # 显示文件大小
        if output_path.exists():
            size_mb = output_path.stat().st_size / 1024 / 1024
            print(f"文件大小: {size_mb:.2f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 视频生成失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except FileNotFoundError:
        print("\n✗ ffmpeg 未安装，请先安装: sudo apt install ffmpeg")
        return False


if __name__ == "__main__":
    # 默认参数
    image_path = "/home/ubuntu/infinigen/outputs/hello_room/coarse/frames/Image/camera_0/Image_0_0_0001_0.png"
    output_path = "/home/ubuntu/infinigen/outputs/hello_room/coarse/video_static.mp4"
    duration = 5  # 5秒
    fps = 24      # 24fps
    
    # 可以从命令行参数获取
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    if len(sys.argv) > 2:
        fps = int(sys.argv[2])
    
    print("="*60)
    print("生成视频")
    print("="*60)
    
    success = create_video_from_image(image_path, output_path, duration, fps)
    
    if success:
        print("\n" + "="*60)
        print("完成！")
        print("="*60)
        print(f"视频文件: {output_path}")
    else:
        sys.exit(1)
