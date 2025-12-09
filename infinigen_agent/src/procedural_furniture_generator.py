"""
程序化家具生成器模块
用于在场景中程序化生成家具（当静态资产中缺失时）
支持在生成时直接指定颜色
"""
import bpy
import numpy as np
from typing import Dict, Optional, List, Tuple
import sys
from pathlib import Path

# 添加 infinigen 路径
infinigen_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(infinigen_root))

# 导入各种家具Factory
from infinigen.assets.objects.seating import (
    BedFactory,
    SofaFactory,
    ChairFactory,
    ArmChairFactory,
    OfficeChairFactory,
    BarChairFactory,
)
from infinigen.assets.objects.tables import (
    TableDiningFactory,
    CoffeeTableFactory,
    SideTableFactory,
    TableCocktailFactory,
)
from infinigen.assets.objects.shelves import (
    SingleCabinetFactory,
    SimpleBookcaseFactory,
    SimpleDeskFactory,
    TVStandFactory,
    LargeShelfFactory,
)
from infinigen.core.util.random import random_general as rg


class ProceduralFurnitureGenerator:
    """程序化家具生成器"""
    
    # 家具类型到Factory的映射
    FURNITURE_FACTORY_MAP: Dict[str, type] = {
        # 座椅类
        "bed": BedFactory,
        "sofa": SofaFactory,
        "couch": SofaFactory,
        "chair": ChairFactory,
        "dining_chair": ChairFactory,
        "armchair": ArmChairFactory,
        "office_chair": OfficeChairFactory,
        "bar_chair": BarChairFactory,
        
        # 桌子类
        "table": TableDiningFactory,
        "dining_table": TableDiningFactory,
        "coffee_table": CoffeeTableFactory,
        "side_table": SideTableFactory,
        "cocktail_table": TableCocktailFactory,
        
        # 柜子/书架类
        "cabinet": SingleCabinetFactory,
        "single_cabinet": SingleCabinetFactory,
        "bookshelf": SimpleBookcaseFactory,
        "bookcase": SimpleBookcaseFactory,
        "shelf": SimpleBookcaseFactory,
        "desk": SimpleDeskFactory,
        "tv_stand": TVStandFactory,
        "large_shelf": LargeShelfFactory,
    }
    
    def __init__(self, factory_seed: Optional[int] = None, coarse: bool = False):
        """
        初始化程序化家具生成器
        
        Args:
            factory_seed: 工厂种子（用于随机生成），如果为None则随机生成
            coarse: 是否使用粗糙模式（快速生成，质量较低）
        """
        if factory_seed is None:
            factory_seed = np.random.randint(1, 1e9)
        self.factory_seed = factory_seed
        self.coarse = coarse
        self.generated_objects: Dict[str, List[bpy.types.Object]] = {}
    
    def get_factory_class(self, furniture_type: str) -> Optional[type]:
        """
        根据家具类型获取对应的Factory类
        
        Args:
            furniture_type: 家具类型名称（如 "bed", "sofa"）
            
        Returns:
            Factory类，如果未找到则返回None
        """
        furniture_type_lower = furniture_type.lower()
        
        # 直接查找
        if furniture_type_lower in self.FURNITURE_FACTORY_MAP:
            return self.FURNITURE_FACTORY_MAP[furniture_type_lower]
        
        # 尝试部分匹配
        for key, factory_class in self.FURNITURE_FACTORY_MAP.items():
            if key in furniture_type_lower or furniture_type_lower in key:
                return factory_class
        
        return None
    
    def generate_furniture(
        self,
        furniture_type: str,
        location: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        color: Optional[Tuple[int, int, int]] = None,
        **factory_kwargs
    ) -> Optional[bpy.types.Object]:
        """
        生成单个家具对象
        
        Args:
            furniture_type: 家具类型（如 "bed", "sofa"）
            location: 生成位置 (x, y, z)
            rotation: 旋转角度 (x, y, z) 弧度
            **factory_kwargs: 传递给Factory的其他参数
            
        Returns:
            生成的Blender对象，失败返回None
        """
        factory_class = self.get_factory_class(furniture_type)
        
        if factory_class is None:
            print(f"⚠ 未找到 {furniture_type} 对应的Factory类")
            return None
        
        try:
            # 创建Factory实例
            # 检查Factory是否支持coarse参数
            import inspect
            sig = inspect.signature(factory_class.__init__)
            if 'coarse' in sig.parameters:
                factory = factory_class(factory_seed=self.factory_seed, coarse=self.coarse)
            else:
                # 如果不支持coarse参数，只传factory_seed
                factory = factory_class(factory_seed=self.factory_seed)
            
            # 生成家具（使用spawn_asset方法）
            # 使用一个随机索引来生成不同的变体
            asset_index = np.random.randint(0, 1000)
            
            obj = factory.spawn_asset(
                i=asset_index,
                loc=location,
                rot=rotation,
                **factory_kwargs
            )
            
            # 设置对象名称
            obj.name = f"{furniture_type}_{asset_index}"
            
            # 如果指定了颜色，立即应用
            if color is not None:
                self.apply_color_to_object(obj, color)
                print(f"✓ 成功生成程序化家具并应用颜色: {furniture_type} -> {obj.name}")
            else:
                print(f"✓ 成功生成程序化家具: {furniture_type} -> {obj.name}")
            
            # 记录生成的对象
            if furniture_type not in self.generated_objects:
                self.generated_objects[furniture_type] = []
            self.generated_objects[furniture_type].append(obj)
            
            return obj
            
        except Exception as e:
            print(f"✗ 生成 {furniture_type} 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_furniture_list(
        self,
        furniture_types: List[str],
        locations: Optional[List[Tuple[float, float, float]]] = None,
        **factory_kwargs
    ) -> Dict[str, List[bpy.types.Object]]:
        """
        批量生成多个家具
        
        Args:
            furniture_types: 家具类型列表
            locations: 位置列表（如果为None，则使用默认位置）
            **factory_kwargs: 传递给Factory的其他参数
            
        Returns:
            生成的家具字典，键为家具类型，值为对象列表
        """
        if locations is None:
            locations = [(0, 0, 0)] * len(furniture_types)
        
        if len(locations) != len(furniture_types):
            print(f"⚠ 位置列表长度 ({len(locations)}) 与家具类型列表长度 ({len(furniture_types)}) 不匹配")
            locations = [(0, 0, 0)] * len(furniture_types)
        
        generated = {}
        
        for furniture_type, location in zip(furniture_types, locations):
            obj = self.generate_furniture(
                furniture_type=furniture_type,
                location=location,
                **factory_kwargs
            )
            
            if obj:
                if furniture_type not in generated:
                    generated[furniture_type] = []
                generated[furniture_type].append(obj)
        
        return generated
    
    def get_available_furniture_types(self) -> List[str]:
        """
        获取所有可用的家具类型列表
        
        Returns:
            家具类型名称列表
        """
        return list(self.FURNITURE_FACTORY_MAP.keys())
    
    def is_furniture_type_supported(self, furniture_type: str) -> bool:
        """
        检查某个家具类型是否支持程序化生成
        
        Args:
            furniture_type: 家具类型名称
            
        Returns:
            是否支持
        """
        return self.get_factory_class(furniture_type) is not None
    
    def apply_color_to_object(self, obj: bpy.types.Object, rgb: Tuple[int, int, int]):
        """
        将颜色应用到对象
        
        Args:
            obj: Blender对象
            rgb: RGB颜色值 (0-255)
        """
        import bpy
        
        # 归一化RGB值到0-1范围
        rgb_normalized = (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, 1.0)
        
        # 获取或创建材质
        material_name = f"{obj.name}_material"
        material = bpy.data.materials.get(material_name)
        
        if not material:
            material = bpy.data.materials.new(name=material_name)
            material.use_nodes = True
        
        # 清除现有节点（保留输出节点）
        material.node_tree.nodes.clear()
        
        # 创建输出节点
        output_node = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (300, 0)
        
        # 创建Principled BSDF节点
        bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # 设置Base Color
        bsdf.inputs['Base Color'].default_value = rgb_normalized
        
        # 连接节点
        material.node_tree.links.new(
            bsdf.outputs['BSDF'],
            output_node.inputs['Surface']
        )
        
        # 应用到对象
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
