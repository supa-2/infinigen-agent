"""
颜色提取和解析模块
从大模型的输出中提取家具颜色信息
"""
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FurnitureColor:
    """家具颜色信息"""
    furniture_type: str  # 家具类型，如 "床", "沙发", "桌子"
    color_name: str  # 颜色名称，如 "白色", "原木色"
    rgb: Optional[Tuple[int, int, int]] = None  # RGB 值
    hex_color: Optional[str] = None  # 十六进制颜色


class ColorParser:
    """颜色解析器"""
    
    # 常见颜色名称到 RGB 的映射
    COLOR_MAP = {
        # 基础颜色
        "白色": (255, 255, 255),
        "黑色": (0, 0, 0),
        "灰色": (128, 128, 128),
        "深灰色": (64, 64, 64),
        "浅灰色": (192, 192, 192),
        
        # 暖色调
        "米白色": (245, 245, 220),
        "米色": (245, 245, 220),
        "奶油色": (255, 253, 208),
        "原木色": (210, 180, 140),
        "浅棕色": (205, 133, 63),
        "深棕色": (101, 67, 33),
        "咖啡色": (139, 69, 19),
        
        # 北欧风格常用色
        "北欧白": (250, 250, 250),
        "北欧灰": (200, 200, 200),
        "浅木色": (222, 184, 135),
        "深木色": (139, 90, 43),
        
        # 其他常见色
        "蓝色": (0, 0, 255),
        "浅蓝色": (173, 216, 230),
        "深蓝色": (0, 0, 139),
        "绿色": (0, 128, 0),
        "浅绿色": (144, 238, 144),
        "深绿色": (0, 100, 0),
        "红色": (255, 0, 0),
        "浅红色": (255, 182, 193),
        "深红色": (139, 0, 0),
        "黄色": (255, 255, 0),
        "浅黄色": (255, 255, 224),
        "橙色": (255, 165, 0),
    }
    
    # 常见家具类型关键词（支持中英文）
    FURNITURE_KEYWORDS = [
        # 中文
        "床", "床头柜", "床架",
        "沙发", "茶几", "电视柜",
        "餐桌", "餐椅", "椅子",
        "书桌", "书柜", "书架",
        "衣柜", "储物柜", "柜子",
        "窗帘", "地毯", "地板",
        "墙壁", "墙面", "墙",
        "灯具", "台灯", "吊灯",
        # 英文
        "bed", "nightstand", "bedframe",
        "sofa", "couch", "table", "coffee_table", "dining_table",
        "chair", "dining_chair",
        "desk", "bookshelf", "bookcase",
        "wardrobe", "closet", "cabinet",
        "curtain", "curtains", "rug", "carpet", "floor",
        "wall", "walls",
        "light", "lamp", "ceiling_light", "chandelier",
    ]
    
    def parse_colors_from_text(self, text: str) -> List[FurnitureColor]:
        """
        从文本中解析家具颜色信息（支持RGB值和颜色名称）
        
        Args:
            text: 大模型输出的文本
            
        Returns:
            家具颜色列表
        """
        colors = []
        
        # 方法1: 尝试解析 JSON 格式（可能包含RGB）
        json_colors = self._parse_json_format(text)
        if json_colors:
            return json_colors
        
        # 方法2: 解析RGB格式（优先，因为大模型输出RGB值）
        rgb_colors = self._parse_rgb_format(text)
        if rgb_colors:
            return rgb_colors
        
        # 方法3: 解析自然语言格式（颜色名称）
        natural_colors = self._parse_natural_format(text)
        if natural_colors:
            return natural_colors
        
        # 方法4: 使用正则表达式提取
        regex_colors = self._parse_regex_format(text)
        return regex_colors
    
    def _parse_json_format(self, text: str) -> List[FurnitureColor]:
        """解析 JSON 格式的颜色信息（支持RGB数组和颜色名称）"""
        try:
            # 尝试提取 JSON 部分
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                colors = []
                
                if isinstance(data, dict):
                    for furniture, color_info in data.items():
                        # 清理家具名称（去掉引号）
                        furniture_clean = furniture.strip('"\'')
                        
                        if isinstance(color_info, (list, tuple)) and len(color_info) == 3:
                            # RGB数组格式: {"床": [255, 255, 255]}
                            r, g, b = color_info
                            if all(0 <= c <= 255 for c in [r, g, b]):
                                rgb = (int(r), int(g), int(b))
                                color_name = self._rgb_to_color_name(rgb)
                                colors.append(FurnitureColor(
                                    furniture_type=furniture_clean,
                                    color_name=color_name,
                                    rgb=rgb,
                                    hex_color=self._rgb_to_hex(rgb)
                                ))
                        elif isinstance(color_info, dict):
                            # 字典格式: {"床": {"color": "白色", "rgb": [255,255,255]}}
                            color_name = color_info.get("color", color_info.get("颜色", ""))
                            rgb = color_info.get("rgb") or color_info.get("RGB")
                            hex_color = color_info.get("hex") or color_info.get("hex_color")
                            
                            if rgb and isinstance(rgb, (list, tuple)) and len(rgb) == 3:
                                rgb = tuple(int(c) for c in rgb)
                            elif color_name:
                                rgb = self.COLOR_MAP.get(color_name)
                            
                            if color_name or rgb:
                                colors.append(self._create_furniture_color(
                                    furniture_clean, color_name or "自定义色", rgb, hex_color
                                ))
                        elif isinstance(color_info, str):
                            # 字符串格式: {"床": "白色"} - 尝试从颜色名称映射
                            color_name = color_info
                            rgb = self.COLOR_MAP.get(color_name)
                            if rgb:
                                colors.append(self._create_furniture_color(
                                    furniture_clean, color_name, rgb
                                ))
                
                if colors:
                    return colors
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            pass
        
        return []
    
    def _parse_natural_format(self, text: str) -> List[FurnitureColor]:
        """解析自然语言格式的颜色信息"""
        colors = []
        
        # 匹配模式：家具 + 颜色
        patterns = [
            r'([^，,。.\n]+?)(?:的|是|为|采用)([^，,。.\n]+?色)',
            r'([^：:]+?)[：:]([^，,。.\n]+?色)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                furniture = match.group(1).strip()
                color_name = match.group(2).strip()
                
                # 检查是否是有效的家具和颜色
                if self._is_valid_furniture(furniture) and self._is_valid_color(color_name):
                    colors.append(self._create_furniture_color(furniture, color_name))
        
        return colors
    
    def _parse_rgb_format(self, text: str) -> List[FurnitureColor]:
        """
        解析RGB格式的颜色信息
        
        支持的格式：
        - 床: (255, 255, 255)
        - 床: RGB(255, 255, 255)
        - 床: 255, 255, 255
        - 床: [255, 255, 255]
        - 床: rgb(255,255,255)
        - {"床": [255, 255, 255]}
        """
        colors = []
        
        # 模式1: 家具名称: (R, G, B) 或 家具名称: RGB(R, G, B)
        pattern1 = r'([^：:\n,]+?)[：:]\s*(?:RGB\s*)?\(?\s*(\d+)\s*[,，]\s*(\d+)\s*[,，]\s*(\d+)\s*\)?'
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            furniture = match.group(1).strip()
            r = int(match.group(2))
            g = int(match.group(3))
            b = int(match.group(4))
            
            # 验证RGB值范围
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                rgb = (r, g, b)
                # 尝试从RGB反推颜色名称（可选）
                color_name = self._rgb_to_color_name(rgb)
                colors.append(FurnitureColor(
                    furniture_type=furniture,
                    color_name=color_name,
                    rgb=rgb,
                    hex_color=self._rgb_to_hex(rgb)
                ))
        
        # 模式2: 家具名称: [R, G, B] 或 家具名称: R, G, B
        pattern2 = r'([^：:\n,]+?)[：:]\s*\[?\s*(\d+)\s*[,，]\s*(\d+)\s*[,，]\s*(\d+)\s*\]?'
        matches = re.finditer(pattern2, text)
        for match in matches:
            furniture = match.group(1).strip()
            r = int(match.group(2))
            g = int(match.group(3))
            b = int(match.group(4))
            
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                rgb = (r, g, b)
                color_name = self._rgb_to_color_name(rgb)
                colors.append(FurnitureColor(
                    furniture_type=furniture,
                    color_name=color_name,
                    rgb=rgb,
                    hex_color=self._rgb_to_hex(rgb)
                ))
        
        # 注意：JSON格式的RGB数组已在 _parse_json_format 中处理，这里不再重复
        
        return colors
    
    def _rgb_to_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """
        从RGB值反推最接近的颜色名称
        
        Args:
            rgb: RGB值
            
        Returns:
            最接近的颜色名称
        """
        r, g, b = rgb
        min_distance = float('inf')
        closest_color = "自定义色"
        
        for color_name, color_rgb in self.COLOR_MAP.items():
            # 计算欧氏距离
            distance = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb)) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        # 如果距离太大，返回RGB描述
        if min_distance > 50:  # 阈值可调
            return f"RGB({r},{g},{b})"
        
        return closest_color
    
    def _parse_regex_format(self, text: str) -> List[FurnitureColor]:
        """使用正则表达式提取颜色信息"""
        colors = []
        
        # 查找所有包含颜色的句子
        sentences = re.split(r'[。.\n]', text)
        for sentence in sentences:
            # 查找家具关键词
            for furniture_keyword in self.FURNITURE_KEYWORDS:
                if furniture_keyword in sentence:
                    # 查找颜色关键词
                    for color_name, rgb in self.COLOR_MAP.items():
                        if color_name in sentence:
                            colors.append(self._create_furniture_color(
                                furniture_keyword, color_name, rgb
                            ))
                            break
        
        return colors
    
    def _create_furniture_color(
        self,
        furniture: str,
        color_name: str,
        rgb: Optional[Tuple[int, int, int]] = None,
        hex_color: Optional[str] = None
    ) -> FurnitureColor:
        """创建家具颜色对象"""
        # 如果没有提供 RGB，从颜色映射中查找
        if rgb is None:
            rgb = self.COLOR_MAP.get(color_name)
        
        # 如果没有提供 hex，从 RGB 计算
        if hex_color is None and rgb:
            hex_color = self._rgb_to_hex(rgb)
        
        return FurnitureColor(
            furniture_type=furniture,
            color_name=color_name,
            rgb=rgb,
            hex_color=hex_color
        )
    
    def _is_valid_furniture(self, text: str) -> bool:
        """检查是否是有效的家具名称"""
        return any(keyword in text for keyword in self.FURNITURE_KEYWORDS)
    
    def _is_valid_color(self, text: str) -> bool:
        """检查是否是有效的颜色名称"""
        return any(color in text for color in self.COLOR_MAP.keys())
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """将 RGB 转换为十六进制"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def format_colors_for_display(self, colors: List[FurnitureColor]) -> str:
        """格式化颜色信息用于显示"""
        lines = []
        for color in colors:
            line = f"{color.furniture_type}: {color.color_name}"
            if color.rgb:
                line += f" (RGB: {color.rgb})"
            if color.hex_color:
                line += f" ({color.hex_color})"
            lines.append(line)
        return "\n".join(lines)
    
    def parse_colors_from_dict(self, color_data: Dict) -> List[FurnitureColor]:
        """
        从字典格式解析颜色信息
        
        Args:
            color_data: 包含颜色信息的字典，格式：
                {
                    "furniture_colors": [
                        {
                            "furniture": "床",
                            "color": "白色",
                            "rgb": [255, 255, 255],
                            "hex": "#FFFFFF"
                        }
                    ]
                }
                
        Returns:
            家具颜色列表
        """
        colors = []
        
        if isinstance(color_data, dict):
            furniture_colors = color_data.get("furniture_colors", [])
            
            for item in furniture_colors:
                if isinstance(item, dict):
                    furniture = item.get("furniture", "")
                    color_name = item.get("color", "")
                    rgb = item.get("rgb")
                    hex_color = item.get("hex") or item.get("hex_color")
                    
                    # 处理 RGB
                    if rgb and isinstance(rgb, (list, tuple)) and len(rgb) == 3:
                        rgb = tuple(int(c) for c in rgb)
                    elif color_name:
                        rgb = self.COLOR_MAP.get(color_name)
                    
                    # 处理 hex
                    if not hex_color and rgb:
                        hex_color = self._rgb_to_hex(rgb)
                    
                    if furniture and (color_name or rgb):
                        colors.append(FurnitureColor(
                            furniture_type=furniture,
                            color_name=color_name or "自定义色",
                            rgb=rgb,
                            hex_color=hex_color
                        ))
        
        return colors


if __name__ == "__main__":
    # 测试颜色解析器
    parser = ColorParser()
    
    test_text = """
    北欧风格卧室色彩方案：
    1. 床：北欧白
    2. 床头柜：浅木色
    3. 墙壁：米白色
    4. 窗帘：浅灰色
    5. 地板：深木色
    """
    
    colors = parser.parse_colors_from_text(test_text)
    print("解析结果:")
    print(parser.format_colors_for_display(colors))

