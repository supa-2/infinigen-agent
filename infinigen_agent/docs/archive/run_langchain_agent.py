#!/usr/bin/env python
"""
运行 LangChain Infinigen Agent
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.langchain_agent import LangChainInfinigenAgent

def main():
    """主函数"""
    print("=" * 60)
    print("LangChain Infinigen Agent")
    print("=" * 60)
    
    # 初始化 Agent
    agent = LangChainInfinigenAgent(
        infinigen_root="/home/ubuntu/infinigen",
        glm_api_key="sk-QEBvsYNQh6pvLotdR4DK1w",
        glm_base_url="https://llmapi.paratera.com"
    )
    
    if len(sys.argv) > 1:
        # 命令行模式
        user_input = " ".join(sys.argv[1:])
        print(f"\n用户输入: {user_input}\n")
        
        result = agent.process_request(
            user_input=user_input,
            output_folder="/home/ubuntu/infinigen/outputs/langchain_test",
            timeout=600  # 10分钟超时
        )
        
        if result.get("success"):
            print("\n" + "=" * 60)
            print("✓ 成功！")
            print("=" * 60)
            print(f"场景文件: {result['scene_file']}")
            print(f"渲染图片: {result['rendered_image']}")
            print(f"应用颜色数: {result['colors_applied']}")
        else:
            print("\n" + "=" * 60)
            print("✗ 失败")
            print("=" * 60)
            print(f"错误: {result.get('error')}")
            print(f"消息: {result.get('message')}")
            if result.get('suggestion'):
                print(f"建议: {result['suggestion']}")
    else:
        # 交互式模式
        agent.interactive_mode()

if __name__ == "__main__":
    main()
