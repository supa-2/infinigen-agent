#!/usr/bin/env python3
"""简单测试 Agent 流程"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("开始测试...")
try:
    from src.agent import InfinigenAgent
    
    agent = InfinigenAgent()
    print("✓ Agent 初始化成功")
    
    print("\n测试生成色彩方案...")
    color_scheme = agent.generate_color_scheme("生成一个北欧风的卧室")
    
    print("\n测试解析颜色...")
    colors = agent.parse_colors(color_scheme)
    
    print(f"\n✓ 成功！解析到 {len(colors)} 个家具颜色")
    for i, c in enumerate(colors[:5], 1):
        print(f"  {i}. {c.furniture_type}: {c.color_name} {c.rgb}")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
