#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("快速测试场景生成功能")
print("="*60)
print()

try:
    print("[1] 测试导入...")
    from src.scene_generator import SceneGenerator
    from src.agent import InfinigenAgent
    print("   ✓ 导入成功")
    
    print("\n[2] 测试场景生成器初始化...")
    infinigen_root = Path("/home/ubuntu/infinigen")
    if infinigen_root.exists():
        gen = SceneGenerator(str(infinigen_root))
        print(f"   ✓ 初始化成功")
        print(f"   根目录: {gen.infinigen_root}")
    else:
        print(f"   ✗ Infinigen 根目录不存在: {infinigen_root}")
        sys.exit(1)
    
    print("\n[3] 测试 Agent 初始化...")
    agent = InfinigenAgent(infinigen_root=str(infinigen_root))
    print("   ✓ Agent 初始化成功")
    
    if agent.scene_generator:
        print(f"   ✓ 场景生成器已附加")
        print(f"   根目录: {agent.scene_generator.infinigen_root}")
    else:
        print("   ⚠ 场景生成器未附加")
    
    print("\n" + "="*60)
    print("✓ 基础功能测试通过！")
    print("="*60)
    print("\n现在可以测试完整流程:")
    print('  python run_agent.py "生成一个北欧风的卧室" \\')
    print('      --auto-generate \\')
    print('      --output-folder /tmp/test_room \\')
    print('      --render-image')
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
