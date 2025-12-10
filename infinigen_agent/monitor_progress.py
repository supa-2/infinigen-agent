#!/usr/bin/env python
"""监控测试进度"""
import os
import time
from pathlib import Path
from datetime import datetime

def find_latest_test_dir():
    """查找最新的测试目录"""
    outputs_dir = Path("/home/ubuntu/infinigen/outputs")
    test_dirs = list(outputs_dir.glob("test_langchain_*"))
    if not test_dirs:
        return None
    # 按修改时间排序，返回最新的
    return max(test_dirs, key=lambda p: p.stat().st_mtime)

def check_progress(test_dir):
    """检查测试进度"""
    if not test_dir or not test_dir.exists():
        return None
    
    progress = {
        "dir": str(test_dir),
        "scene_file": None,
        "scene_size": None,
        "render_dir": None,
        "render_count": 0,
        "has_assets": False,
        "stage": "unknown"
    }
    
    # 检查场景文件
    scene_file = test_dir / "scene.blend"
    if not scene_file.exists():
        scene_file = test_dir / "coarse" / "scene.blend"
    
    if scene_file.exists():
        progress["scene_file"] = str(scene_file)
        progress["scene_size"] = scene_file.stat().st_size / (1024 * 1024)  # MB
        progress["stage"] = "场景已生成"
    
    # 检查 assets 目录
    assets_dir = test_dir / "assets"
    if assets_dir.exists():
        progress["has_assets"] = True
        if not progress["scene_file"]:
            progress["stage"] = "正在生成场景（terrain阶段）"
    
    # 检查渲染目录
    render_dirs = list(test_dir.glob("frames_render_*"))
    if render_dirs:
        render_dir = render_dirs[0]
        progress["render_dir"] = str(render_dir)
        render_files = list(render_dir.glob("*.png")) + list(render_dir.glob("*.exr"))
        progress["render_count"] = len(render_files)
        if progress["render_count"] > 0:
            progress["stage"] = "渲染完成"
        else:
            progress["stage"] = "正在渲染"
    
    return progress

def main():
    print("=" * 60)
    print("测试进度监控")
    print("=" * 60)
    print("按 Ctrl+C 停止监控\n")
    
    last_progress = None
    try:
        while True:
            test_dir = find_latest_test_dir()
            
            if not test_dir:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ 未找到测试目录")
                time.sleep(5)
                continue
            
            progress = check_progress(test_dir)
            
            if progress != last_progress:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📁 测试目录: {Path(progress['dir']).name}")
                print(f"   阶段: {progress['stage']}")
                
                if progress['has_assets']:
                    print(f"   ✅ Assets 目录已创建")
                
                if progress['scene_file']:
                    print(f"   ✅ 场景文件: {Path(progress['scene_file']).name} ({progress['scene_size']:.2f} MB)")
                
                if progress['render_dir']:
                    print(f"   📸 渲染目录: {Path(progress['render_dir']).name}")
                    print(f"      渲染文件数: {progress['render_count']}")
                
                last_progress = progress
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")

if __name__ == "__main__":
    main()
