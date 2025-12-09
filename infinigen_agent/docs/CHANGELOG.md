# 更新日志

## 2024-12-06

### 新增功能
- ✅ 支持选择是否使用 `/v1` 路径
- ✅ 自动尝试两种 API 路径（带 `/v1` 和不带 `/v1`）
- ✅ 改进错误处理和调试信息

### 配置更新
- `config/api_config.py` 中新增 `USE_V1_PATH` 配置项
- 默认设置为 `False`（不使用 `/v1` 路径）
- 可以通过修改配置或传递参数来选择路径

### 使用方法

#### 方法1: 修改配置文件
编辑 `config/api_config.py`:
```python
USE_V1_PATH = False  # 不使用 /v1
# 或
USE_V1_PATH = True   # 使用 /v1
```

#### 方法2: 在代码中指定
```python
from src.vllm_client import VLLMClient

# 不使用 /v1
client = VLLMClient(use_v1=False)

# 使用 /v1
client = VLLMClient(use_v1=True)
```

### 测试
运行测试脚本会自动尝试两种路径：
```bash
python test_vllm.py
```

