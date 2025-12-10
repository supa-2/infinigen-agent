#!/usr/bin/env python3
"""
从已生成的场景文件继续处理（应用颜色和渲染）
用于恢复中断的流程
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.langchain_agent import LangChainInfinigenAgent

def main():
    if len(sys.argv) < 2:
        print("用法: python continue_from_scene.py <场景文件路径> [用户输入]")
        print("示例: python continue_from_scene.py outputs/interactive_1765333976/scene.blend '生成一个北欧风格的卧室'")
        sys.exit(1)
    
    scene_file = sys.argv[1]
    user_input = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 60)
    print("从已有场景文件继续处理")
    print("=" * 60)
    print(f"场景文件: {scene_file}")
    if user_input:
        print(f"用户输入: {user_input}")
    print("=" * 60 + "\n")
    
    agent = LangChainInfinigenAgent()
    
    result = agent.process_existing_scene(
        scene_file=scene_file,
        user_input=user_input
    )
    
    print("\n" + "=" * 60)
    if result.get("success"):
        print("✓ 处理完成！")
        print("=" * 60)
        print(f"场景文件: {result['scene_file']}")
        if 'rendered_image' in result:
            print(f"渲染图片: {result['rendered_image']}")
    else:
        print("✗ 处理失败")
        print("=" * 60)
        print(f"错误: {result.get('error')}")
        print(f"消息: {result.get('message')}")
    print("=" * 60)

if __name__ == "__main__":
    main()

