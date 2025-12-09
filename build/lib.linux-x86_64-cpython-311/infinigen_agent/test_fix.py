#!/usr/bin/env python3
"""测试场景生成器初始化修复"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("测试场景生成器初始化修复")
print("="*60)

try:
    from src.agent import InfinigenAgent
    
    print("\n[测试1] 不指定 infinigen_root（自动检测）")
    agent1 = InfinigenAgent()
    if agent1.scene_generator:
        print(f"  ✓ 场景生成器已初始化")
        print(f"  根目录: {agent1.scene_generator.infinigen_root}")
    else:
        print("  ✗ 场景生成器未初始化")
    
    print("\n[测试2] 手动指定 infinigen_root")
    agent2 = InfinigenAgent(infinigen_root="/home/ubuntu/infinigen")
    if agent2.scene_generator:
        print(f"  ✓ 场景生成器已初始化")
        print(f"  根目录: {agent2.scene_generator.infinigen_root}")
    else:
        print("  ✗ 场景生成器未初始化")
    
    print("\n" + "="*60)
    if agent1.scene_generator or agent2.scene_generator:
        print("✓ 修复成功！场景生成器可以正常初始化")
    else:
        print("✗ 修复失败，场景生成器仍无法初始化")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
