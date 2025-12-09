#!/usr/bin/env python3
"""简单测试场景生成器"""
import sys
from pathlib import Path
import traceback

sys.path.insert(0, str(Path(__file__).parent))

print("开始测试...", flush=True)

try:
    print("1. 导入模块...", flush=True)
    from src.scene_generator import SceneGenerator
    print("   ✓ SceneGenerator 导入成功", flush=True)
    
    print("\n2. 初始化场景生成器...", flush=True)
    # 手动指定 Infinigen 根目录
    infinigen_root = Path(__file__).parent.parent
    print(f"   尝试 Infinigen 根目录: {infinigen_root}", flush=True)
    
    if not infinigen_root.exists():
        print(f"   ✗ 目录不存在: {infinigen_root}", flush=True)
        sys.exit(1)
    
    generator = SceneGenerator(str(infinigen_root))
    print(f"   ✓ 场景生成器初始化成功", flush=True)
    print(f"   Infinigen 根目录: {generator.infinigen_root}", flush=True)
    
    print("\n3. 测试 Agent 初始化...", flush=True)
    from src.agent import InfinigenAgent
    
    agent = InfinigenAgent(infinigen_root=str(infinigen_root))
    print("   ✓ Agent 初始化成功", flush=True)
    
    if agent.scene_generator:
        print(f"   ✓ 场景生成器已附加: {agent.scene_generator.infinigen_root}", flush=True)
    else:
        print("   ⚠ 场景生成器未附加", flush=True)
    
    print("\n" + "="*60, flush=True)
    print("✓ 基础测试通过！", flush=True)
    print("="*60, flush=True)
    print("\n提示: 场景生成需要较长时间，可以运行完整测试:", flush=True)
    print("  python test_auto_generate.py", flush=True)
    
except Exception as e:
    print(f"\n✗ 错误: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
