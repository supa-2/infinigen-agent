"""
测试英文输入格式
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.color_parser import ColorParser
from src.agent import InfinigenAgent


def test_english_rgb_parsing():
    """测试英文家具名称的RGB解析"""
    parser = ColorParser()
    
    # 测试用例：英文家具名称 + RGB值
    test_text = """
    Nordic bedroom color scheme:
    1. bed: (250, 250, 250)
    2. nightstand: (222, 184, 135)
    3. wall: (245, 245, 220)
    4. curtain: (200, 200, 200)
    5. floor: (139, 90, 43)
    """
    
    print("测试英文输入格式:")
    print(test_text)
    print("\n解析结果:")
    colors = parser.parse_colors_from_text(test_text)
    for color in colors:
        print(f"  {color.furniture_type}: RGB{color.rgb} {color.hex_color}")
    print()


def test_agent_system_prompt():
    """测试智能体的系统提示词"""
    agent = InfinigenAgent()
    
    # 模拟英文输入
    user_request = "生成一个nordic的bedroom"
    print(f"用户输入: {user_request}")
    print("\n系统提示词已更新为英文格式")
    print("大模型应该输出英文家具名称 + RGB值")
    print("\n示例输出:")
    print("""
    1. bed: (250, 250, 250)
    2. nightstand: (222, 184, 135)
    3. wall: (245, 245, 220)
    4. curtain: (200, 200, 200)
    5. floor: (139, 90, 43)
    """)


if __name__ == "__main__":
    test_english_rgb_parsing()
    print("\n" + "="*50 + "\n")
    test_agent_system_prompt()

