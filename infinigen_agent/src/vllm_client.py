"""
vLLM API 客户端
用于与 vLLM 服务进行交互
"""
import requests
import json
import time
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.api_config import (
    VLLM_API_URL,
    VLLM_API_URL_NO_V1,
    VLLM_API_KEY,
    API_TIMEOUT,
    MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    USE_V1_PATH
)


class VLLMClient:
    """vLLM API 客户端类"""
    
    def __init__(
        self,
        api_url: str = None,
        api_key: str = VLLM_API_KEY,
        timeout: int = API_TIMEOUT,
        use_v1: bool = USE_V1_PATH
    ):
        """
        初始化 vLLM 客户端
        
        Args:
            api_url: vLLM API 端点（如果为 None，根据 use_v1 自动选择）
            api_key: API 密钥
            timeout: 请求超时时间
            use_v1: 是否使用 /v1 路径
        """
        if api_url is None:
            self.api_url = VLLM_API_URL if use_v1 else VLLM_API_URL_NO_V1
        else:
            self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.use_v1 = use_v1
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        retries: int = MAX_RETRIES
    ) -> Optional[Dict[str, Any]]:
        """
        发送 HTTP 请求（带重试机制）
        
        Args:
            endpoint: API 端点（如 "chat/completions"）
            data: 请求数据
            retries: 剩余重试次数
            
        Returns:
            API 响应数据，失败返回 None
        """
        # 根据是否使用 v1 路径构建 URL
        if self.use_v1:
            url = f"{self.api_url}/{endpoint}"
        else:
            # 不使用 v1 时，直接拼接端点
            url = f"{self.api_url}/{endpoint}"
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout,
                    verify=False  # 如果证书有问题，可能需要设置为 False
                )
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError:
                    # 如果不是 JSON，打印响应内容用于调试
                    print(f"响应不是 JSON 格式，状态码: {response.status_code}")
                    print(f"响应内容: {response.text[:500]}")
                    return None
            except requests.exceptions.Timeout:
                print(f"请求超时，剩余重试次数: {retries - attempt - 1}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    print("达到最大重试次数，请求失败")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                if hasattr(e.response, 'text'):
                    print(f"响应内容: {e.response.text}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
        
        return None
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        发送聊天补全请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数
            
        Returns:
            API 响应，包含生成的文本
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response = self._make_request("chat/completions", data)
        return response
    
    def get_completion_text(self, response: Dict[str, Any]) -> Optional[str]:
        """
        从 API 响应中提取生成的文本
        
        Args:
            response: API 响应
            
        Returns:
            生成的文本内容
        """
        if not response:
            return None
        
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            print(f"解析响应失败: {e}")
            print(f"响应内容: {response}")
            return None
    
    def simple_chat(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """
        简单的聊天接口
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            **kwargs: 其他参数
            
        Returns:
            模型生成的回复文本
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})
        
        response = self.chat_completion(messages, **kwargs)
        return self.get_completion_text(response)
    
    def test_connection(self) -> bool:
        """
        测试 API 连接
        
        Returns:
            连接是否成功
        """
        try:
            response = self.simple_chat(
                "Hello, this is a test message.",
                max_tokens=10
            )
            if response:
                print(f"✓ API 连接成功！模型回复: {response}")
                return True
            else:
                print("✗ API 连接失败：无法获取响应")
                return False
        except Exception as e:
            print(f"✗ API 连接失败：{e}")
            return False


if __name__ == "__main__":
    # 测试客户端
    print("正在测试 vLLM API 连接...")
    client = VLLMClient()
    client.test_connection()

