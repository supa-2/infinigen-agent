"""
测试 vLLM API 连接和模型列表
"""
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.vllm_client import VLLMClient
import requests


def list_models():
    """列出可用的模型"""
    api_url = "https://service.thuarchdog.com:58889/v1"
    api_key = "sk-Z0MdU0NAXCmiwYF_3io5kXtwl8cxHEtGciRtopREtFsDMXLMkjHxLGlBTX8"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{api_url}/models",
            headers=headers,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        models = response.json()
        print("可用的模型列表:")
        print(json.dumps(models, indent=2, ensure_ascii=False))
        return models
    except Exception as e:
        print(f"获取模型列表失败: {e}")
        return None


def test_chat():
    """测试聊天功能"""
    print("\n" + "="*50)
    print("测试 vLLM API 连接...")
    print("="*50)
    
    # 先尝试列出模型
    print("\n1. 获取可用模型列表...")
    models = list_models()
    
    # 测试两种路径
    for use_v1 in [False, True]:
        print(f"\n2. 测试聊天功能 (使用 /v1: {use_v1})...")
        client = VLLMClient(use_v1=use_v1)
        print(f"   API URL: {client.api_url}")
        
        test_message = "你好，请简单介绍一下你自己。"
        print(f"   发送消息: {test_message}")
        
        try:
            response = client.simple_chat(
                test_message,
                max_tokens=100
            )
            
            if response:
                print(f"\n✓ 模型回复: {response}")
                print(f"\n✓ 成功！使用的路径: {'/v1' if use_v1 else '无 /v1'}")
                return True
            else:
                print(f"   ✗ 无法获取回复 (使用 /v1: {use_v1})")
        except Exception as e:
            print(f"   ✗ 错误: {e}")
    
    print("\n✗ 所有路径都失败")
    return False


if __name__ == "__main__":
    import json
    test_chat()

