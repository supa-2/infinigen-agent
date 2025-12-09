#!/usr/bin/env python3
"""
完整 Agent 流程测试
测试从用户输入到颜色解析的完整流程
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import InfinigenAgent

print("="*60)
print("完整 Agent 流程测试")
print("="*60)

try:
    # 创建 Agent
    print("\n[步骤1] 初始化 Agent...")
    print("-" * 60)
    agent = InfinigenAgent()
    print("✓ Agent 初始化成功")
    
    # 测试2: 生成色彩方案
    print("\n[步骤2] 生成色彩方案")
    print("-" * 60)
    user_request = "生成一个北欧风的卧室"
    print(f"用户请求: {user_request}")
    
    color_scheme = agent.generate_color_scheme(user_request)
    
    if not color_scheme:
        print("✗ 色彩方案生成失败")
        sys.exit(1)
    
    print("✓ 色彩方案生成成功")
    
    # 测试3: 解析颜色
    print("\n[步骤3] 解析颜色")
    print("-" * 60)
    colors = agent.parse_colors(color_scheme)
    
    if not colors:
        print("✗ 颜色解析失败：未解析出颜色信息")
        sys.exit(1)
    
    print(f"✓ 颜色解析成功！解析到 {len(colors)} 个家具颜色:")
    print()
    for i, color in enumerate(colors[:10], 1):  # 显示前10个
        rgb_str = f"RGB{color.rgb}" if color.rgb else "无RGB"
        print(f"  {i}. {color.furniture_type:15s} → {color.color_name:15s} ({rgb_str})")
    
    if len(colors) > 10:
        print(f"  ... 还有 {len(colors) - 10} 个家具颜色")
    
    # 测试总结
    print("\n" + "="*60)
    print("✓ 完整流程测试成功！")
    print("="*60)
    print("\n测试结果:")
    print(f"  ✓ vLLM 连接正常")
    print(f"  ✓ 色彩方案生成正常")
    print(f"  ✓ 颜色解析正常")
    print(f"  ✓ 共解析出 {len(colors)} 个家具颜色")
    print("\n系统已就绪，可以使用以下命令运行完整流程:")
    print('  python run_agent.py "生成一个北欧风的卧室" ../outputs/hello_room/coarse/scene.blend')
    
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
