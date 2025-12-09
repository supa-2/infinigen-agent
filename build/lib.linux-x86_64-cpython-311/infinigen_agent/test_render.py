#!/usr/bin/env python
"""
测试渲染功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 添加 infinigen 路径
infinigen_root = project_root.parent
sys.path.insert(0, str(infinigen_root))

from src.scene_renderer import SceneRenderer
import bpy


def test_render_image():
    """测试渲染图片"""
    print("="*60)
    print("测试1: 渲染图片")
    print("="*60)
    
    scene_path = "../outputs/hello_room/coarse/scene.blend"
    
    if not Path(scene_path).exists():
        print(f"✗ 场景文件不存在: {scene_path}")
        return False
    
    try:
        # 清除当前场景（如果已加载）
        bpy.ops.wm.read_homefile(app_template="")
        
        renderer = SceneRenderer(scene_path)
        
        # 渲染图片（使用较低分辨率以加快速度）
        output_image = "../outputs/hello_room/coarse/rendered_test.png"
        print(f"\n正在渲染图片到: {output_image}")
        print("分辨率: 1280x720 (测试用)")
        
        result = renderer.render_image(
            output_path=output_image,
            resolution=(1280, 720)
        )
        
        if Path(result).exists():
            print(f"✓ 图片渲染成功: {result}")
            print(f"文件大小: {Path(result).stat().st_size / 1024:.2f} KB")
            return True
        else:
            print(f"✗ 图片文件未生成: {result}")
            return False
            
    except Exception as e:
        print(f"✗ 渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_render_video():
    """测试渲染视频"""
    print("\n" + "="*60)
    print("测试2: 渲染视频")
    print("="*60)
    
    scene_path = "../outputs/hello_room/coarse/scene.blend"
    
    if not Path(scene_path).exists():
        print(f"✗ 场景文件不存在: {scene_path}")
        return False
    
    # 检查 ffmpeg
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ ffmpeg 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ffmpeg 未安装，跳过视频测试")
        print("  安装方法: sudo apt install ffmpeg")
        return False
    
    try:
        # 清除当前场景
        bpy.ops.wm.read_homefile(app_template="")
        
        renderer = SceneRenderer(scene_path)
        
        # 渲染视频（使用少量帧以加快速度）
        output_folder = "../outputs/hello_room/coarse/video_test"
        print(f"\n正在渲染视频到: {output_folder}")
        print("帧数: 10 (测试用)")
        print("帧率: 24 fps")
        print("分辨率: 1280x720")
        
        result = renderer.render_and_create_video(
            output_folder=output_folder,
            num_frames=10,  # 测试用，只渲染10帧
            fps=24,
            resolution=(1280, 720)
        )
        
        if Path(result).exists():
            print(f"✓ 视频渲染成功: {result}")
            print(f"文件大小: {Path(result).stat().st_size / 1024 / 1024:.2f} MB")
            return True
        else:
            print(f"✗ 视频文件未生成: {result}")
            return False
            
    except Exception as e:
        print(f"✗ 渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试渲染功能...")
    print(f"当前工作目录: {Path.cwd()}")
    
    # 测试图片渲染
    image_success = test_render_image()
    
    # 测试视频渲染
    video_success = test_render_video()
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"图片渲染: {'✓ 成功' if image_success else '✗ 失败'}")
    print(f"视频渲染: {'✓ 成功' if video_success else '✗ 失败'}")
    print("="*60)

