#!/usr/bin/env python
"""
直接测试渲染功能
"""
import sys
import bpy
from pathlib import Path

# 添加路径
infinigen_root = Path(__file__).parent.parent
sys.path.insert(0, str(infinigen_root))

from infinigen.core.rendering.render import render_image
from infinigen.core.placement import camera as cam_util


def main():
    scene_path = infinigen_root / "outputs/hello_room/coarse/scene.blend"
    
    print("="*60)
    print("测试渲染功能")
    print("="*60)
    print(f"场景文件: {scene_path}")
    
    if not scene_path.exists():
        print(f"✗ 场景文件不存在")
        return
    
    print(f"✓ 场景文件存在 ({scene_path.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # 加载场景
    print("\n正在加载场景...")
    try:
        bpy.ops.wm.open_mainfile(filepath=str(scene_path))
        print("✓ 场景加载成功")
    except Exception as e:
        print(f"✗ 加载失败: {e}")
        return
    
    # 查找相机
    cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
    if cameras:
        camera = cameras[0]
        print(f"✓ 找到相机: {camera.name}")
    else:
        if bpy.context.scene.camera:
            camera = bpy.context.scene.camera
            print(f"✓ 使用场景默认相机: {camera.name}")
        else:
            print("✗ 未找到相机")
            return
    
    # 设置分辨率（测试用，较低分辨率）
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    print(f"\n分辨率: {bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}")
    
    # 渲染图片
    output_folder = infinigen_root / "outputs/hello_room/coarse/render_test"
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"\n正在渲染图片到: {output_folder}")
    print("这可能需要几分钟...")
    
    try:
        render_image(
            camera=camera,
            frames_folder=output_folder,
            passes_to_save=["Image"]
        )
        
        # 检查输出
        image_files = list(output_folder.glob("**/*.png"))
        if image_files:
            print(f"\n✓ 渲染成功！")
            print(f"生成了 {len(image_files)} 个图片文件:")
            for img in image_files[:5]:
                print(f"  - {img.name} ({img.stat().st_size / 1024:.2f} KB)")
        else:
            print("\n⚠ 未找到图片文件，检查输出文件夹...")
            print(f"输出文件夹内容: {list(output_folder.iterdir())}")
            
    except Exception as e:
        print(f"\n✗ 渲染失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

