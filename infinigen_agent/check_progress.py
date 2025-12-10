#!/usr/bin/env python
"""快速检查测试进度"""
from pathlib import Path
from datetime import datetime

def check_test_progress():
    """检查最新的测试进度"""
    outputs_dir = Path("/home/ubuntu/infinigen/outputs")
    test_dirs = list(outputs_dir.glob("test_langchain_*"))
    
    if not test_dirs:
        print("⚠ 未找到测试目录")
        return
    
    # 按修改时间排序
    latest_dir = max(test_dirs, key=lambda p: p.stat().st_mtime)
    
    print("=" * 60)
    print(f"📁 最新测试目录: {latest_dir.name}")
    print(f"   修改时间: {datetime.fromtimestamp(latest_dir.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 检查 assets
    assets_dir = latest_dir / "assets"
    if assets_dir.exists():
        print("✅ Assets 目录: 已创建")
        mountain_dir = assets_dir / "MultiMountains" / "0"
        if mountain_dir.exists():
            finish_file = mountain_dir / "finish"
            if finish_file.exists():
                print("   ✅ Terrain 生成完成")
            else:
                print("   ⏳ Terrain 正在生成...")
    else:
        print("⏳ Assets 目录: 尚未创建")
    
    print()
    
    # 检查场景文件
    scene_file = latest_dir / "scene.blend"
    if not scene_file.exists():
        scene_file = latest_dir / "coarse" / "scene.blend"
    
    if scene_file.exists():
        size_mb = scene_file.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(scene_file.stat().st_mtime)
        print(f"✅ 场景文件: {scene_file.name}")
        print(f"   大小: {size_mb:.2f} MB")
        print(f"   生成时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("⏳ 场景文件: 尚未生成（正在生成中...）")
    
    print()
    
    # 检查渲染
    render_dirs = list(latest_dir.glob("frames_render_*"))
    if render_dirs:
        render_dir = render_dirs[0]
        render_files = list(render_dir.glob("*.png")) + list(render_dir.glob("*.exr"))
        print(f"📸 渲染目录: {render_dir.name}")
        print(f"   渲染文件数: {len(render_files)}")
        if render_files:
            latest_render = max(render_files, key=lambda p: p.stat().st_mtime)
            size_mb = latest_render.stat().st_size / (1024 * 1024)
            print(f"   最新文件: {latest_render.name} ({size_mb:.2f} MB)")
    else:
        print("⏳ 渲染: 尚未开始")
    
    print()
    
    # 检查其他文件
    pipeline_file = latest_dir / "pipeline_coarse.csv"
    if pipeline_file.exists():
        print("✅ Pipeline 文件: 已生成")
    
    solve_state = latest_dir / "solve_state.json"
    if solve_state.exists():
        print("✅ Solve state: 已生成")

if __name__ == "__main__":
    check_test_progress()
