#!/usr/bin/env python
"""检查场景生成测试的进度"""
from pathlib import Path
from datetime import datetime

def check_scene_gen_progress():
    """检查场景生成测试的进度"""
    output_dir = Path("/home/ubuntu/infinigen/outputs/test_scene_generation")
    
    print("=" * 60)
    print("场景生成测试进度检查")
    print("=" * 60)
    print(f"输出目录: {output_dir}")
    print()
    
    if not output_dir.exists():
        print("⏳ 输出目录尚未创建，场景生成可能刚刚开始...")
        return
    
    # 检查是否有 coarse 子目录
    coarse_dir = output_dir / "coarse"
    if coarse_dir.exists():
        print(f"✅ Coarse 目录: {coarse_dir}")
        
        # 检查场景文件
        scene_file = coarse_dir / "scene.blend"
        if scene_file.exists():
            size_mb = scene_file.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(scene_file.stat().st_mtime)
            print(f"✅ 场景文件: {scene_file}")
            print(f"   大小: {size_mb:.2f} MB")
            print(f"   修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("⏳ 场景文件: 尚未生成")
        
        # 检查 pipeline 文件
        pipeline_file = coarse_dir / "pipeline_coarse.csv"
        if pipeline_file.exists():
            print(f"✅ Pipeline 文件: {pipeline_file}")
            # 读取最后几行
            try:
                with open(pipeline_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        print(f"   Pipeline 行数: {len(lines) - 1}")
                        print(f"   最后阶段: {lines[-1].strip().split(',')[0] if lines[-1] else 'N/A'}")
            except Exception as e:
                print(f"   ⚠ 无法读取 pipeline 文件: {e}")
        else:
            print("⏳ Pipeline 文件: 尚未生成")
    else:
        print("⏳ Coarse 目录: 尚未创建")
    
    # 列出所有文件
    print()
    print("当前目录内容:")
    for item in sorted(output_dir.iterdir()):
        if item.is_file():
            size = item.stat().st_size
            size_str = f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.2f} MB"
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            print(f"  📄 {item.name} ({size_str}, {mtime.strftime('%H:%M:%S')})")
        elif item.is_dir():
            item_count = len(list(item.rglob('*')))
            print(f"  📁 {item.name}/ ({item_count} 项)")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    check_scene_gen_progress()

