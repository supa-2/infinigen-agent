"""
vLLM API 配置文件
"""
# vLLM API 端点配置
# 如果连接有问题，可以尝试去掉 /v1，使用基础 URL
VLLM_API_BASE_URL = "https://service.thuarchdog.com:58889"
VLLM_API_URL = f"{VLLM_API_BASE_URL}/v1"  # 默认使用 /v1
VLLM_API_URL_NO_V1 = VLLM_API_BASE_URL  # 不使用 /v1 的版本
VLLM_API_KEY = "sk-Z0MdU0NAXCmiwYF_3io5kXtwl8cxHEtGciRtopREtFsDMXLMkjHxLGlBTX8"

# 是否使用 /v1 路径（如果连接失败，可以设置为 False）
USE_V1_PATH = True  # 使用 /v1 路径（已确认正确）

# API 请求配置
API_TIMEOUT = 60  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数

# 模型配置
DEFAULT_MODEL = "Qwen2.5-7B-infinigen"  # vLLM 部署的模型名称
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000

