"""
房间类型检测器
根据用户输入智能识别房间类型
"""
from typing import Optional, List

# 官方支持的房间类型（来自 infinigen/core/tags.py）
ROOM_TYPES = {
    "Kitchen": ["kitchen", "厨房", "cooking", "cook"],
    "Bedroom": ["bedroom", "bed", "卧室", "sleep", "sleeping"],
    "LivingRoom": ["living room", "livingroom", "lounge", "客厅", "起居室"],
    "Bathroom": ["bathroom", "bath", "restroom", "toilet", "卫生间", "浴室"],
    "DiningRoom": ["dining room", "diningroom", "dining", "餐厅", "饭厅"],
    "Closet": ["closet", "wardrobe", "衣橱", "衣柜"],
    "Hallway": ["hallway", "hall", "corridor", "走廊", "过道"],
    "Garage": ["garage", "车库"],
    "Balcony": ["balcony", "阳台"],
    "Utility": ["utility", "utility room", "工具间"],
    "StaircaseRoom": ["staircase", "stairs", "楼梯"],
    "Office": ["office", "study", "书房", "工作室"],
    "MeetingRoom": ["meeting room", "会议室"],
    "OpenOffice": ["open office", "openoffice", "开放办公室"],
    "BreakRoom": ["break room", "breakroom", "休息室"],
    "Restroom": ["restroom", "公共卫生间"],
    "FactoryOffice": ["factory office", "工厂办公室"],
    "Warehouse": ["warehouse", "仓库"],
}


def detect_room_type(user_request: str) -> Optional[str]:
    """
    根据用户输入检测房间类型
    
    Args:
        user_request: 用户请求文本
        
    Returns:
        房间类型名称（如 "Bedroom", "Kitchen"），如果未检测到则返回 None
    """
    user_request_lower = user_request.lower()
    
    # 按优先级排序（常用房间类型优先）
    priority_rooms = ["Bedroom", "Kitchen", "LivingRoom", "Bathroom", "DiningRoom"]
    other_rooms = [room for room in ROOM_TYPES.keys() if room not in priority_rooms]
    
    # 先检查常用房间类型
    for room_type in priority_rooms + other_rooms:
        keywords = ROOM_TYPES[room_type]
        for keyword in keywords:
            if keyword.lower() in user_request_lower:
                return room_type
    
    return None


def detect_room_types(user_request: str) -> List[str]:
    """
    检测用户输入中可能包含的多个房间类型
    
    Args:
        user_request: 用户请求文本
        
    Returns:
        房间类型列表
    """
    user_request_lower = user_request.lower()
    detected_rooms = []
    
    for room_type, keywords in ROOM_TYPES.items():
        for keyword in keywords:
            if keyword.lower() in user_request_lower:
                if room_type not in detected_rooms:
                    detected_rooms.append(room_type)
                break
    
    return detected_rooms

