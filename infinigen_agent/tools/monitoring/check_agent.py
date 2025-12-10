#!/usr/bin/env python
"""检查 Agent 配置"""
import sys
import logging
from pathlib import Path

# 设置日志级别
logging.basicConfig(level=logging.INFO)

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("检查 LangChain Agent 配置")
print("=" * 60)

# 1. 检查配置文件
print("\n1. 检查配置文件...")
try:
    from config.api_config import VLLM_API_URL, VLLM_API_KEY, DEFAULT_MODEL
    print(f"   ✓ 配置文件加载成功")
    print(f"     vLLM API URL: {VLLM_API_URL}")
    print(f"     vLLM API Key: {VLLM_API_KEY[:20]}...")
    print(f"     默认模型: {DEFAULT_MODEL}")
except Exception as e:
    print(f"   ✗ 配置文件加载失败: {e}")
    import traceback
    traceback.print_exc()

# 2. 检查导入
print("\n2. 检查导入...")
try:
    from src.langchain_agent import LangChainInfinigenAgent
    print("   ✓ LangChainInfinigenAgent 导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试初始化
print("\n3. 测试初始化...")
try:
    agent = LangChainInfinigenAgent(
        infinigen_root="/home/ubuntu/infinigen"
    )
    print("   ✓ Agent 初始化成功")
    print(f"     Infinigen 根目录: {agent.infinigen_root}")
    print(f"     GLM 模型: {agent.glm_llm.model_name}")
    print(f"     GLM API: {agent.glm_llm.base_url}")
    print(f"     Qwen 模型: {agent.qwen_llm.model_name}")
    print(f"     Qwen API: {agent.qwen_llm.base_url}")
except Exception as e:
    print(f"   ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ 配置检查完成")
print("=" * 60)
