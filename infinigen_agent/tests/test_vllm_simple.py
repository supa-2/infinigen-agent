#!/usr/bin/env python
"""
简单的 vLLM 测试
"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 确保输出立即刷新
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

print("="*60, flush=True)
print("vLLM API 连接测试", flush=True)
print("="*60, flush=True)

# 创建客户端
print("\n1. 创建 vLLM 客户端...")
client = VLLMClient()
print(f"   API URL: {client.api_url}")
print(f"   使用 /v1 路径: {client.use_v1}")

# 测试连接
print("\n2. 测试 API 连接...")
test_message = "你好，请简单介绍一下你自己。"
print(f"   发送消息: {test_message}")

try:
    response = client.simple_chat(
        test_message,
        max_tokens=100
    )
    
    if response:
        print(f"\n✓ 成功！")
        print(f"   模型回复: {response}")
    else:
        print("\n✗ 无法获取回复")
        
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
