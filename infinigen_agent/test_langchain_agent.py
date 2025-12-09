#!/usr/bin/env python
"""测试 LangChain Infinigen Agent - 完整流程测试"""
import sys
from pathlib import Path
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.langchain_agent import LangChainInfinigenAgent
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)


def test_full_workflow():
    """测试完整工作流程（场景生成 + 颜色应用 + 渲染）"""
    print("=" * 60)
    print("LangChain Infinigen Agent - 完整流程测试")
    print("=" * 60)
    print("⚠ 注意：此测试需要 5-15 分钟")
    print("=" * 60)
    
    # 初始化 Agent
    print("\n初始化 Agent...")
    try:
        agent = LangChainInfinigenAgent(
            infinigen_root="/home/ubuntu/infinigen"
        )
        print("✓ Agent 初始化成功")
        print(f"  GLM 模型: {agent.glm_llm.model_name}")
        print(f"  Qwen 模型: {agent.qwen_llm.model_name}")
    except Exception as e:
        print(f"✗ Agent 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试参数
    user_input = "生成一个现代风格的客厅，沙发是蓝色的，茶几是白色的"
    output_folder = f"/home/ubuntu/infinigen/outputs/test_langchain_{int(time.time())}"
    
    print(f"\n用户输入: {user_input}")
    print(f"输出文件夹: {output_folder}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        result = agent.process_request(
            user_input=user_input,
            output_folder=output_folder,
            seed=None,  # 使用随机种子
            timeout=900  # 15分钟超时
        )
        
        print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.get("success"):
            print("\n" + "=" * 60)
            print("✓ 完整流程测试成功！")
            print("=" * 60)
            print(f"场景文件: {result['scene_file']}")
            print(f"渲染图片: {result['rendered_image']}")
            print(f"应用颜色数: {result['colors_applied']}")
            if result.get('color_scheme'):
                print(f"\n颜色方案预览:")
                print(result['color_scheme'][:300] + "...")
            return True
        else:
            print("\n" + "=" * 60)
            print("✗ 完整流程测试失败")
            print("=" * 60)
            print(f"错误: {result.get('error')}")
            print(f"消息: {result.get('message')}")
            if result.get('scene_file'):
                print(f"\n注意: 场景文件已生成: {result['scene_file']}")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠ 测试被用户中断")
        return False
    except Exception as e:
        print(f"\n✗ 完整流程测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)
