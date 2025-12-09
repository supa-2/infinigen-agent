#!/usr/bin/env python3
"""
测试自动生成场景功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agent import InfinigenAgent

print("="*60)
print("测试自动生成场景功能")
print("="*60)

try:
    # 创建 Agent（自动检测 Infinigen 根目录）
    print("\n[步骤1] 初始化 Agent...")
    agent = InfinigenAgent()
    
    if not agent.scene_generator:
        print("⚠ 场景生成器未初始化")
        print("  请确保 Infinigen 根目录正确")
        print("  或手动指定: agent = InfinigenAgent(infinigen_root='/path/to/infinigen')")
        sys.exit(1)
    
    print("✓ Agent 初始化成功")
    print(f"  Infinigen 根目录: {agent.scene_generator.infinigen_root}")
    
    # 测试生成场景（使用较短的超时时间进行测试）
    print("\n[步骤2] 测试场景生成...")
    print("  注意: 场景生成可能需要几分钟时间")
    
    output_folder = "/tmp/test_auto_generate"
    user_request = "生成一个北欧风的卧室"
    
    print(f"  用户请求: {user_request}")
    print(f"  输出文件夹: {output_folder}")
    
    # 只测试场景生成，不渲染（节省时间）
    scene_file = agent.generate_scene_from_request(
        user_request=user_request,
        output_folder=output_folder,
        seed=0,
        timeout=600  # 10分钟超时
    )
    
    print(f"\n✓ 场景生成成功！")
    print(f"  场景文件: {scene_file}")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n现在可以使用完整流程:")
    print(f'  python run_agent.py "{user_request}" --auto-generate --output-folder {output_folder} --render-image')
    
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
