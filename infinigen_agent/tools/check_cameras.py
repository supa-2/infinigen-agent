#!/usr/bin/env python3
"""
检查场景中的相机
"""
import sys
from pathlib import Path
import bpy

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_cameras(scene_path: str):
    """检查场景中的相机"""
    print(f"正在加载场景: {scene_path}")
    bpy.ops.wm.open_mainfile(filepath=scene_path)
    
    cameras = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            cameras.append(obj)
        # 也查找相机rig
        elif 'camera' in obj.name.lower() or 'cam' in obj.name.lower():
            # 检查是否有子对象是相机
            for child in obj.children:
                if child.type == 'CAMERA':
                    cameras.append(child)
    
    if not cameras:
        if bpy.context.scene.camera:
            cameras.append(bpy.context.scene.camera)
    
    print(f"\n找到 {len(cameras)} 个相机:")
    for i, cam in enumerate(cameras, 1):
        print(f"  {i}. {cam.name}")
        print(f"     位置: {cam.location}")
        print(f"     旋转: {cam.rotation_euler}")
    
    return cameras

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_cameras.py <scene.blend>")
        sys.exit(1)
    
    scene_path = sys.argv[1]
    cameras = check_cameras(scene_path)

