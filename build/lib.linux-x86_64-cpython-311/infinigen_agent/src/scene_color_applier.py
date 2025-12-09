"""
Infinigen 场景颜色应用模块
将提取的颜色应用到 Blender 场景中的家具上
"""
import bpy
import bmesh
from typing import List, Dict, Optional
from src.color_parser import FurnitureColor


class SceneColorApplier:
    """场景颜色应用器"""
    
    def __init__(self, scene_path: Optional[str] = None):
        """
        初始化场景颜色应用器
        
        Args:
            scene_path: Blender 场景文件路径（.blend 文件）
        """
        self.scene_path = scene_path
        if scene_path:
            self.load_scene(scene_path)
    
    def load_scene(self, scene_path: str):
        """加载 Blender 场景"""
        try:
            bpy.ops.wm.open_mainfile(filepath=scene_path)
            print(f"✓ 成功加载场景: {scene_path}")
        except Exception as e:
            print(f"✗ 加载场景失败: {e}")
            raise
    
    def find_objects_by_name(self, keywords: List[str]) -> List[bpy.types.Object]:
        """
        根据关键词查找场景中的对象
        
        Args:
            keywords: 关键词列表，如 ["床", "沙发"]
            
        Returns:
            匹配的对象列表
        """
        found_objects = []
        
        # 关键词映射（支持中英文家具名称）
        keyword_map = {
            # 中文
            "床": ["bed", "Bed", "BED"],
            "床头柜": ["nightstand", "Nightstand", "bedside"],
            "沙发": ["sofa", "Sofa", "SOFA", "couch"],
            "茶几": ["table", "Table", "coffee_table", "CoffeeTable"],
            "电视柜": ["tv", "TV", "tv_stand", "TVStand"],
            "餐桌": ["dining_table", "DiningTable", "table"],
            "餐椅": ["chair", "Chair", "dining_chair"],
            "书桌": ["desk", "Desk", "DESK"],
            "书柜": ["bookshelf", "Bookshelf", "bookcase"],
            "书架": ["bookshelf", "Bookshelf", "bookcase"],
            "衣柜": ["wardrobe", "Wardrobe", "closet"],
            "储物柜": ["cabinet", "Cabinet", "storage"],
            "柜子": ["cabinet", "Cabinet", "cabinet"],
            "窗帘": ["curtain", "Curtain", "curtains"],
            "地毯": ["rug", "Rug", "carpet"],
            "地板": ["floor", "Floor", "ground"],
            "墙壁": ["wall", "Wall", "walls"],
            "墙面": ["wall", "Wall", "walls"],
            "墙": ["wall", "Wall", "walls"],
            "灯具": ["light", "Light", "lamp"],
            "台灯": ["lamp", "Lamp", "table_lamp"],
            "吊灯": ["ceiling_light", "CeilingLight", "chandelier"],
            # 英文（直接映射）
            "bed": ["bed", "Bed", "BED"],
            "nightstand": ["nightstand", "Nightstand", "bedside"],
            "sofa": ["sofa", "Sofa", "SOFA", "couch"],
            "couch": ["sofa", "Sofa", "SOFA", "couch"],
            "table": ["table", "Table", "coffee_table", "CoffeeTable", "dining_table"],
            "coffee_table": ["table", "Table", "coffee_table", "CoffeeTable"],
            "dining_table": ["dining_table", "DiningTable", "table"],
            "chair": ["chair", "Chair", "dining_chair"],
            "desk": ["desk", "Desk", "DESK"],
            "bookshelf": ["bookshelf", "Bookshelf", "bookcase"],
            "bookcase": ["bookshelf", "Bookshelf", "bookcase"],
            "wardrobe": ["wardrobe", "Wardrobe", "closet"],
            "closet": ["wardrobe", "Wardrobe", "closet"],
            "cabinet": ["cabinet", "Cabinet", "storage"],
            "curtain": ["curtain", "Curtain", "curtains"],
            "curtains": ["curtain", "Curtain", "curtains"],
            "rug": ["rug", "Rug", "carpet"],
            "carpet": ["rug", "Rug", "carpet"],
            "floor": ["floor", "Floor", "ground"],
            "wall": ["wall", "Wall", "walls"],
            "walls": ["wall", "Wall", "walls"],
            "light": ["light", "Light", "lamp"],
            "lamp": ["lamp", "Lamp", "table_lamp"],
            "ceiling_light": ["ceiling_light", "CeilingLight", "chandelier"],
            "chandelier": ["ceiling_light", "CeilingLight", "chandelier"],
        }
        
        # 收集所有可能的搜索词
        search_terms = []
        for keyword in keywords:
            if keyword in keyword_map:
                search_terms.extend(keyword_map[keyword])
            else:
                search_terms.append(keyword)
        
        # 在场景中查找对象
        for obj in bpy.context.scene.objects:
            obj_name_lower = obj.name.lower()
            for term in search_terms:
                if term.lower() in obj_name_lower:
                    if obj not in found_objects:
                        found_objects.append(obj)
                    break
        
        return found_objects
    
    def apply_color_to_object(
        self,
        obj: bpy.types.Object,
        color: FurnitureColor,
        material_name: Optional[str] = None
    ):
        """
        将颜色应用到对象
        
        Args:
            obj: Blender 对象
            color: 颜色信息
            material_name: 材质名称（可选）
        """
        if not color.rgb:
            print(f"警告: {color.furniture_type} 没有有效的 RGB 值")
            return
        
        # 确保对象处于活动状态
        bpy.context.view_layer.objects.active = obj
        
        # 获取或创建材质
        if material_name is None:
            material_name = f"{obj.name}_material"
        
        # 检查材质是否已存在
        material = bpy.data.materials.get(material_name)
        if not material:
            material = bpy.data.materials.new(name=material_name)
        
        # 确保材质使用节点
        material.use_nodes = True
        nodes = material.node_tree.nodes
        
        # 清除默认节点（保留输出节点）
        for node in nodes:
            if node.type != 'OUTPUT_MATERIAL':
                nodes.remove(node)
        
        # 创建 Principled BSDF 节点
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # 设置基础颜色
        rgb_normalized = tuple(c / 255.0 for c in color.rgb)
        bsdf.inputs['Base Color'].default_value = (*rgb_normalized, 1.0)
        
        # 连接 BSDF 到输出
        output_node = nodes.get('Material Output')
        if output_node:
            material.node_tree.links.new(
                bsdf.outputs['BSDF'],
                output_node.inputs['Surface']
            )
        
        # 将材质应用到对象
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
        
        print(f"✓ 已将颜色应用到 {obj.name}: {color.color_name} (RGB: {color.rgb})")
    
    def apply_colors_to_scene(self, colors: List[FurnitureColor]):
        """
        将颜色列表应用到场景
        
        Args:
            colors: 家具颜色列表
        """
        print(f"\n开始应用 {len(colors)} 个颜色到场景...")
        
        for color in colors:
            # 查找匹配的对象
            objects = self.find_objects_by_name([color.furniture_type])
            
            if objects:
                for obj in objects:
                    self.apply_color_to_object(obj, color)
            else:
                print(f"⚠ 未找到匹配的对象: {color.furniture_type}")
        
        print("\n✓ 颜色应用完成")
    
    def save_scene(self, output_path: str):
        """保存场景"""
        try:
            bpy.ops.wm.save_as_mainfile(filepath=output_path)
            print(f"✓ 场景已保存到: {output_path}")
        except Exception as e:
            print(f"✗ 保存场景失败: {e}")
            raise


if __name__ == "__main__":
    # 测试代码（需要在 Blender 环境中运行）
    print("此模块需要在 Blender 环境中运行")
    print("使用示例:")
    print("  applier = SceneColorApplier('scene.blend')")
    print("  applier.apply_colors_to_scene(colors)")

