"""
测试颜色解析器（RGB格式）
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.color_parser import ColorParser


def test_rgb_parsing():
    """测试RGB格式解析"""
    parser = ColorParser()
    
    # 测试用例1: 标准RGB格式
    test1 = """
    北欧风格卧室色彩方案：
    1. 床: (250, 250, 250)
    2. 床头柜: (222, 184, 135)
    3. 墙壁: (245, 245, 220)
    4. 窗帘: (200, 200, 200)
    5. 地板: (139, 90, 43)
    """
    
    print("测试1: 标准RGB格式")
    print(test1)
    colors1 = parser.parse_colors_from_text(test1)
    print(f"解析结果 ({len(colors1)} 个):")
    for color in colors1:
        print(f"  {color.furniture_type}: {color.color_name} RGB{color.rgb} {color.hex_color}")
    print()
    
    # 测试用例2: RGB()格式
    test2 = """
    床: RGB(255, 255, 255)
    沙发: RGB(192, 192, 192)
    茶几: RGB(210, 180, 140)
    """
    
    print("测试2: RGB()格式")
    print(test2)
    colors2 = parser.parse_colors_from_text(test2)
    print(f"解析结果 ({len(colors2)} 个):")
    for color in colors2:
        print(f"  {color.furniture_type}: {color.color_name} RGB{color.rgb} {color.hex_color}")
    print()
    
    # 测试用例3: 数组格式
    test3 = """
    床: [255, 255, 255]
    沙发: [200, 200, 200]
    椅子: 128, 128, 128
    """
    
    print("测试3: 数组/逗号格式")
    print(test3)
    colors3 = parser.parse_colors_from_text(test3)
    print(f"解析结果 ({len(colors3)} 个):")
    for color in colors3:
        print(f"  {color.furniture_type}: {color.color_name} RGB{color.rgb} {color.hex_color}")
    print()
    
    # 测试用例4: JSON格式
    test4 = """
    {
        "床": [250, 250, 250],
        "沙发": [200, 200, 200],
        "茶几": [210, 180, 140]
    }
    """
    
    print("测试4: JSON格式")
    print(test4)
    colors4 = parser.parse_colors_from_text(test4)
    print(f"解析结果 ({len(colors4)} 个):")
    for color in colors4:
        print(f"  {color.furniture_type}: {color.color_name} RGB{color.rgb} {color.hex_color}")
    print()


if __name__ == "__main__":
    test_rgb_parsing()

