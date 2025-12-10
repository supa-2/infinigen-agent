#!/usr/bin/env python
"""检查当前测试状态"""
import time
from pathlib import Path
from datetime import datetime

outputs_dir = Path("/home/ubuntu/infinigen/outputs")
test_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith("test_langchain_")]

if not test_dirs:
    print("❌ 未找到测试目录")
    exit(1)

# 找到最新的目录
latest_dir = max(test_dirs, key=lambda p: p.stat().st_mtime)
elapsed_min = (time.time() - latest_dir.stat().st_mtime) / 60

print("=" * 70)
print("🔍 当前测试状态")
print("=" * 70)
print(f"📁 测试目录: {latest_dir.name}")
print(f"⏰ 已运行: {elapsed_min:.1f} 分钟")
print()

# 检查 pipeline_coarse.csv
pipeline_file = latest_dir / "pipeline_coarse.csv"
if pipeline_file.exists():
    print("📋 Pipeline 进度:")
    with open(pipeline_file, "r") as f:
        lines = f.readlines()
        if len(lines) > 1:
            completed = []
            for line in lines[1:]:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    stage_name = parts[1]
                    ran = parts[2].strip().lower() == "true"
                    if ran:
                        completed.append(stage_name)
                    print(f"   {'✅' if ran else '⏳'} {stage_name}")
            
            print(f"\n   完成: {len(completed)}/{len(lines)-1} 阶段")
            if completed:
                print(f"   最后完成: {completed[-1]}")
else:
    print("⚠️  Pipeline 文件不存在（可能还在初始化）")

# 检查场景文件
scene_file = latest_dir / "scene.blend"
if not scene_file.exists():
    scene_file = latest_dir / "coarse" / "scene.blend"

if scene_file.exists():
    print(f"\n✅ 场景文件已生成: {scene_file}")
else:
    print(f"\n⏳ 场景文件尚未生成")

print()
print("=" * 70)
