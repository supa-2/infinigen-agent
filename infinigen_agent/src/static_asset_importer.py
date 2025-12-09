"""
外部资产导入模块
用于在已有场景中导入外部资产并应用颜色

根据 Infinigen 官方文档，导入外部静态资产应该使用 StaticCategoryFactory。
如果对应的 Factory 不存在，则动态创建。
"""
import bpy
import os
from pathlib import Path
from typing import List, Dict, Optional
import sys
import random

# 添加 infinigen 路径
infinigen_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(infinigen_root))

from infinigen.assets.static_assets.base import StaticAssetFactory
from infinigen.assets.static_assets.static_category import static_category_factory
from infinigen.core.util.math import FixedSeed


class StaticAssetImporter:
    """外部资产导入器"""
    
    def __init__(self, scene_path: Optional[str] = None):
        """
        初始化外部资产导入器
        
        Args:
            scene_path: Blender 场景文件路径（.blend 文件）
        """
        self.scene_path = scene_path
        self.factory = StaticAssetFactory(factory_seed=0)
        
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
    
    def import_asset(self, asset_path: str, object_name: Optional[str] = None) -> Optional[bpy.types.Object]:
        """
        导入单个外部资产
        
        Args:
            asset_path: 资产文件路径（支持 .glb, .obj, .fbx, .blend 等）
            object_name: 导入后对象的名称（可选）
            
        Returns:
            导入的对象，失败返回 None
        """
        if not os.path.exists(asset_path):
            print(f"✗ 资产文件不存在: {asset_path}")
            return None
        
        try:
            # 检查文件是否存在且可读
            if not os.path.isfile(asset_path):
                print(f"✗ 资产文件不存在或不是文件: {asset_path}")
                return None
            
            # 检查文件大小（空文件或损坏的文件）
            file_size = os.path.getsize(asset_path)
            if file_size == 0:
                print(f"✗ 资产文件为空: {asset_path}")
                return None
            
            # 检查文件格式（简单检查）
            if asset_path.lower().endswith('.glb') or asset_path.lower().endswith('.gltf'):
                # GLB/GLTF文件应该以特定字节开头
                with open(asset_path, 'rb') as f:
                    header = f.read(4)
                    if asset_path.lower().endswith('.glb'):
                        # GLB文件应该以 "glTF" 开头（二进制格式）
                        if header[:4] != b'glTF':
                            print(f"⚠ 警告: GLB文件格式可能不正确: {asset_path}")
                    elif asset_path.lower().endswith('.gltf'):
                        # GLTF文件是JSON格式，应该以 '{' 或 '[' 开头
                        try:
                            header_str = header.decode('utf-8')
                            if not (header_str.startswith('{') or header_str.startswith('[')):
                                print(f"⚠ 警告: GLTF文件格式可能不正确: {asset_path}")
                        except:
                            pass
            
            imported_obj = self.factory.import_file(asset_path)
            
            if imported_obj and object_name:
                imported_obj.name = object_name
            
            print(f"✓ 成功导入资产: {asset_path}")
            if imported_obj:
                print(f"  对象名称: {imported_obj.name}")
            
            return imported_obj
        except Exception as e:
            print(f"✗ 导入资产失败: {asset_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def import_assets_from_folder(
        self,
        folder_path: str,
        furniture_type: str,
        max_count: int = 1,
        use_factory: bool = True
    ) -> List[bpy.types.Object]:
        """
        从文件夹导入资产（使用 StaticCategoryFactory 或直接导入）
        
        Args:
            folder_path: 资产文件夹路径
            furniture_type: 家具类型（用于命名）
            max_count: 最大导入数量
            use_factory: 是否使用 StaticCategoryFactory（推荐，符合官方文档）
            
        Returns:
            导入的对象列表
        """
        if not os.path.exists(folder_path):
            print(f"✗ 资产文件夹不存在: {folder_path}")
            return []
        
        imported_objects = []
        
        if use_factory:
            # 使用 StaticCategoryFactory（符合官方文档的方式）
            try:
                # 动态创建 Factory
                factory_class = static_category_factory(folder_path)
                factory = factory_class(factory_seed=random.randint(1, 1e9), coarse=False)
                
                # 使用 Factory 创建资产
                for i in range(max_count):
                    try:
                        obj = factory.create_asset()
                        if obj:
                            obj.name = f"{furniture_type}_{i}" if max_count > 1 else furniture_type
                            imported_objects.append(obj)
                            if max_count == 1:
                                break  # 只导入一个
                    except Exception as e:
                        print(f"⚠ 使用 Factory 导入失败，尝试直接导入: {e}")
                        # 如果 Factory 方式失败，回退到直接导入
                        use_factory = False
                        break
            except Exception as e:
                print(f"⚠ 创建 Factory 失败，使用直接导入方式: {e}")
                use_factory = False
        
        if not use_factory or not imported_objects:
            # 回退到直接导入方式（当前方式）
            # 查找支持的资产文件
            supported_extensions = ['.glb', '.gltf', '.obj', '.fbx', '.dae', '.blend', '.ply', '.stl', '.usd', '.abc']
            asset_files = []
            
            for file in os.listdir(folder_path):
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    asset_files.append(os.path.join(folder_path, file))
            
            if not asset_files:
                print(f"✗ 在文件夹中未找到支持的资产文件: {folder_path}")
                return []
            
            # 随机选择文件导入
            selected_files = random.sample(asset_files, min(max_count, len(asset_files)))
            
            for i, asset_file in enumerate(selected_files):
                obj_name = f"{furniture_type}_{i}" if max_count > 1 else furniture_type
                imported_obj = self.import_asset(asset_file, object_name=obj_name)
                if imported_obj:
                    imported_objects.append(imported_obj)
        
        return imported_objects
    
    def import_furniture_assets(
        self,
        furniture_colors: List[Dict],
        static_assets_root: Optional[str] = None
    ) -> Dict[str, List[bpy.types.Object]]:
        """
        根据颜色方案导入家具资产
        
        Args:
            furniture_colors: 家具颜色列表，格式: [{"furniture": "chair", "color": (255, 255, 255), ...}, ...]
            static_assets_root: 静态资产根目录（默认: infinigen/assets/static_assets/source）
            
        Returns:
            导入的对象字典，键为家具类型，值为对象列表
        """
        if static_assets_root is None:
            static_assets_root = infinigen_root / "infinigen" / "assets" / "static_assets" / "source"
        else:
            static_assets_root = Path(static_assets_root)
        
        if not static_assets_root.exists():
            print(f"⚠ 静态资产根目录不存在: {static_assets_root}")
            print("  将尝试在场景中查找现有对象")
            return {}
        
        imported_objects = {}
        
        # 家具类型到文件夹名称的映射（匹配实际的文件夹名称）
        furniture_folder_map = {
            # 座椅类
            "chair": "Chair",
            "chairs": "Chair",
            "dining_chair": "Chair",
            
            # 桌子类
            "table": "Table",
            "dining_table": "Table",
            "coffee_table": "Table",
            
            # 沙发类
            "sofa": "Sofa",
            "couch": "Sofa",
            
            # 床类
            "bed": "Bed",
            "nightstand": "Bed",  # 床头柜可能放在 Bed 文件夹，如果没有单独文件夹
            
            # 柜子类
            "cabinet": "Cabinet",
            "wardrobe": "Cabinet",
            "closet": "Cabinet",
            "shelf": "Shelf",
            "bookshelf": "Shelf",
            "bookcase": "Shelf",
            
            # 时钟类
            "clock": "wallClock",
            "wall_clock": "wallClock",
            "wallclock": "wallClock",
            
            # 装饰类
            "vase": "Decoration",
            "decoration": "Decoration",
            "floor_sculpture": "floorSculpture",
            "sculpture": "floorSculpture",
            "floor_plant": "floorPlant",
            "plant": "floorPlant",
            "wall_art": "wallArt",
            "art": "wallArt",
            "painting": "wallArt",
            
            # 灯具类
            "lamp": "Lighting",
            "light": "Lighting",
            "lighting": "Lighting",
            "ceiling_light": "ceilingHanging",
            "ceiling_hanging": "ceilingHanging",
            "chandelier": "ceilingHanging",
            
            # 浴室类
            "toilet": "Toilet",
            "bathtub": "Bathtub",
            "bath": "Bathtub",
            "sink": "Sink",
            
            # 浴室类
            "toilet": "Toilet",
            "bathtub": "Bathtub",
            "bath": "Bathtub",
            "sink": "Sink",
            
            # 电器类
            "appliance": "Appliance",
            "appliances": "Appliance",
            "tv": "Appliance",
            "television": "Appliance",
            "refrigerator": "Appliance",
            "fridge": "Appliance",
            
            # 其他装饰
            "curtain": "ceilingHanging",  # 窗帘在 ceilingHanging 文件夹
            "curtains": "ceilingHanging",
            "rug": "Decoration",  # 地毯可能放在装饰类
            "carpet": "Decoration",
        }
        
        for furniture_color in furniture_colors:
            furniture_name = furniture_color.get("furniture", "").lower()
            
            # 查找对应的文件夹
            folder_name = furniture_folder_map.get(furniture_name)
            if not folder_name:
                # 尝试直接使用家具名称（首字母大写）
                folder_name = furniture_name.capitalize()
            
            folder_path = static_assets_root / folder_name
            
            if folder_path.exists():
                print(f"\n正在导入 {furniture_name} 从: {folder_path}")
                objects = self.import_assets_from_folder(
                    str(folder_path),
                    furniture_type=furniture_name,
                    max_count=1
                )
                if objects:
                    imported_objects[furniture_name] = objects
            else:
                print(f"⚠ 未找到 {furniture_name} 的资产文件夹: {folder_path}")
        
        return imported_objects
    
    def save_scene(self, output_path: str):
        """保存场景"""
        try:
            bpy.ops.wm.save_as_mainfile(filepath=output_path)
            print(f"✓ 场景已保存到: {output_path}")
        except Exception as e:
            print(f"✗ 保存场景失败: {e}")
            raise

