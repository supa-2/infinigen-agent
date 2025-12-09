#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("开始测试 vLLM...")
print(f"Python 版本: {sys.version}")
print(f"工作目录: {os.getcwd()}")

try:
    print("\n导入模块...")
    from src.vllm_client import VLLMClient
    from config.api_config import VLLM_API_URL, VLLM_API_KEY
    
    print(f"API URL: {VLLM_API_URL}")
    print(f"API Key: {VLLM_API_KEY[:20]}...")
    
    print("\n创建客户端...")
    client = VLLMClient()
    print(f"客户端 API URL: {client.api_url}")
    
    print("\n发送测试消息...")
    test_message = "你好"
    print(f"消息: {test_message}")
    
    response = client.simple_chat(test_message, max_tokens=50)
    
    if response:
        print(f"\n✓ 成功！")
        print(f"回复: {response}")
    else:
        print("\n✗ 未收到回复")
        
except Exception as e:
    print(f"\n✗ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")
