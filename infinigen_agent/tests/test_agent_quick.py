#!/usr/bin/env python
"""快速测试 LangChain Agent"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("LangChain Agent 快速测试")
print("=" * 60)

# 1. 测试导入
print("\n1. 测试导入...")
try:
    from src.langchain_agent import LangChainInfinigenAgent
    print("   ✓ 导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 测试初始化
print("\n2. 测试 Agent 初始化...")
try:
    agent = LangChainInfinigenAgent(
        infinigen_root="/home/ubuntu/infinigen"
    )
    print("   ✓ Agent 初始化成功")
    print(f"     Infinigen 根目录: {agent.infinigen_root}")
    print(f"     GLM 模型: {agent.glm_llm.model_name}")
    print(f"     Qwen 模型: {agent.qwen_llm.model_name}")
    print(f"     Qwen API URL: {agent.qwen_llm.base_url}")
except Exception as e:
    print(f"   ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试输入验证（需要 API 调用）
print("\n3. 测试输入验证...")
print("   输入: '生成一个北欧风的卧室'")
try:
    is_valid, message = agent.validate_user_input("生成一个北欧风的卧室")
    print(f"   ✓ 验证完成")
    print(f"     结果: {'合理' if is_valid else '不合理'}")
    print(f"     消息: {message[:150]}...")
except Exception as e:
    print(f"   ✗ 验证失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 测试颜色生成（需要 API 调用）
print("\n4. 测试颜色生成...")
print("   输入: '生成一个北欧风的卧室，床是白色的，沙发是蓝色的'")
try:
    color_scheme = agent.generate_furniture_colors("生成一个北欧风的卧室，床是白色的，沙发是蓝色的")
    print(f"   ✓ 颜色生成成功")
    print(f"     输出长度: {len(color_scheme)} 字符")
    print(f"     前200字符: {color_scheme[:200]}...")
except Exception as e:
    print(f"   ✗ 颜色生成失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✓ 快速测试完成")
print("=" * 60)
