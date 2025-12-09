#!/usr/bin/env python
"""简单的 LangChain Agent 测试"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("LangChain Agent 简单测试")
print("=" * 60)

# 1. 检查依赖
print("\n1. 检查依赖...")
try:
    import langchain
    print(f"   ✓ langchain: {langchain.__version__}")
except ImportError as e:
    print(f"   ✗ langchain 未安装: {e}")
    print("   请运行: pip install langchain langchain-openai langchain-core")
    sys.exit(1)

try:
    import langchain_openai
    print(f"   ✓ langchain-openai: 已安装")
except ImportError as e:
    print(f"   ✗ langchain-openai 未安装: {e}")
    print("   请运行: pip install langchain-openai")
    sys.exit(1)

# 2. 测试导入
print("\n2. 测试导入...")
try:
    from src.langchain_agent import LangChainInfinigenAgent
    print("   ✓ LangChainInfinigenAgent 导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试初始化
print("\n3. 测试 Agent 初始化...")
try:
    agent = LangChainInfinigenAgent(
        infinigen_root="/home/ubuntu/infinigen",
        glm_api_key="sk-QEBvsYNQh6pvLotdR4DK1w",
        glm_base_url="https://llmapi.paratera.com"
    )
    print("   ✓ Agent 初始化成功")
    print(f"     Infinigen 根目录: {agent.infinigen_root}")
    print(f"     GLM 模型: {agent.glm_llm.model_name}")
    print(f"     Qwen 模型: {agent.qwen_llm.model_name}")
except Exception as e:
    print(f"   ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 测试输入验证（需要 API 调用）
print("\n4. 测试输入验证（需要 API 调用）...")
print("   输入: '生成一个北欧风的卧室'")
try:
    is_valid, message = agent.validate_user_input("生成一个北欧风的卧室")
    print(f"   ✓ 验证完成")
    print(f"     结果: {'合理' if is_valid else '不合理'}")
    print(f"     消息: {message[:100]}...")
except Exception as e:
    print(f"   ✗ 验证失败: {e}")
    print("   （可能是 API 连接问题，但不影响其他功能）")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✓ 基础测试完成")
print("=" * 60)
print("\n提示：")
print("  - 要测试完整流程，运行: python test_langchain_agent.py --full")
print("  - 要运行 Agent，使用: python run_langchain_agent.py '你的场景描述'")
print("=" * 60)
