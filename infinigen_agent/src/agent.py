"""
主智能体系统
整合 vLLM、颜色解析和场景修改功能
"""
import sys
from pathlib import Path
import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vllm_client import VLLMClient
from src.color_parser import ColorParser
from src.scene_color_applier import SceneColorApplier
from src.scene_renderer import SceneRenderer
from src.scene_generator import SceneGenerator
from src.procedural_furniture_generator import ProceduralFurnitureGenerator
from src.room_type_detector import detect_room_type
from typing import List, Optional


class InfinigenAgent:
    """Infinigen 智能体主类"""
    
    def __init__(self, infinigen_root: Optional[str] = None):
        """
        初始化智能体
        
        Args:
            infinigen_root: Infinigen 根目录路径，用于场景生成
        """
        self.vllm_client = VLLMClient()
        self.color_parser = ColorParser()
        self.scene_applier = None
        self.scene_renderer = None
        self.scene_generator = None
        
        # 尝试初始化场景生成器
        try:
            # 如果指定了 infinigen_root，直接使用
            if infinigen_root:
                self.scene_generator = SceneGenerator(infinigen_root)
            else:
                # 自动检测 Infinigen 根目录
                # 假设 infinigen_agent 在 infinigen 目录下
                current_dir = Path(__file__).parent.parent
                if current_dir.name == 'infinigen_agent':
                    auto_root = current_dir.parent
                else:
                    auto_root = Path('/home/ubuntu/infinigen')
                
                # 尝试初始化，如果失败则设为 None
                if auto_root.exists():
                    try:
                        self.scene_generator = SceneGenerator(str(auto_root))
                    except Exception as e:
                        print(f"⚠ 场景生成器初始化失败: {e}")
                        print(f"  尝试的路径: {auto_root}")
                        print("  将无法自动生成场景，需要使用已有场景文件或使用 --infinigen-root 手动指定")
                        self.scene_generator = None
                else:
                    print(f"⚠ 未找到 Infinigen 根目录，自动生成场景功能将不可用")
                    print(f"  尝试的路径: {auto_root}")
                    print("  可以使用 --infinigen-root 手动指定")
                    self.scene_generator = None
        except Exception as e:
            print(f"⚠ 场景生成器初始化失败: {e}")
            print("  将无法自动生成场景，需要使用已有场景文件")
            self.scene_generator = None
    
    def generate_color_scheme(self, user_request: str) -> str:
        """
        根据用户请求生成色彩方案
        
        Args:
            user_request: 用户请求，如 "生成一个北欧风的卧室"
            
        Returns:
            大模型生成的色彩方案文本
        """
        system_prompt = """You are a professional interior designer. The user will describe the room style they want,
your task is to analyze and output RGB color values for various furniture in the room.

Please output in the following format (using RGB values, range 0-255):
1. bed: (255, 255, 255)
2. nightstand: (210, 180, 140)
3. sofa: (200, 200, 200)
4. chair: (192, 192, 192)
5. table: (222, 184, 135)
... (list all major furniture)

RGB value guidelines:
- White tones: (255, 255, 255) or (250, 250, 250)
- Beige/Cream: (245, 245, 220)
- Light wood: (210, 180, 140) or (222, 184, 135)
- Dark wood: (139, 90, 43) or (101, 67, 33)
- Light gray: (192, 192, 192) or (200, 200, 200)
- Dark gray: (64, 64, 64) or (128, 128, 128)

For Nordic style, use: white (250, 250, 250), light wood (222, 184, 135), light gray (200, 200, 200), beige (245, 245, 220).

Please output RGB values directly in the format: furniture_name: (R, G, B), do not add other explanations. Use English furniture names."""
        
        print(f"正在向大模型请求色彩方案...")
        print(f"用户请求: {user_request}")
        
        response = self.vllm_client.simple_chat(
            user_message=user_request,
            system_message=system_prompt,
            max_tokens=1000
        )
        
        if response:
            print(f"\n大模型生成的色彩方案:\n{response}\n")
            return response
        else:
            raise Exception("无法从大模型获取响应")
    
    def parse_colors(self, color_scheme_text: str) -> List:
        """
        解析色彩方案文本，提取颜色信息
        
        Args:
            color_scheme_text: 色彩方案文本
            
        Returns:
            家具颜色列表
        """
        print("正在解析颜色信息...")
        colors = self.color_parser.parse_colors_from_text(color_scheme_text)
        
        if colors:
            print(f"\n解析到 {len(colors)} 个家具颜色:")
            print(self.color_parser.format_colors_for_display(colors))
        else:
            print("⚠ 未能解析出颜色信息")
        
        return colors
    
    def apply_colors_to_scene(
        self,
        scene_path: str,
        colors: List,
        output_path: Optional[str] = None
    ):
        """
        将颜色应用到场景
        
        Args:
            scene_path: 输入场景文件路径
            colors: 家具颜色列表
            output_path: 输出场景文件路径（可选）
        """
        if output_path is None:
            output_path = scene_path.replace('.blend', '_colored.blend')
        
        print(f"\n正在加载场景: {scene_path}")
        self.scene_applier = SceneColorApplier(scene_path)
        
        print("正在应用颜色...")
        self.scene_applier.apply_colors_to_scene(colors)
        
        print(f"正在保存场景: {output_path}")
        self.scene_applier.save_scene(output_path)
        
        return output_path
    
    def process_request(
        self,
        user_request: str,
        scene_path: str,
        output_path: Optional[str] = None,
        use_procedural_generation: bool = True
    ) -> str:
        """
        处理完整的用户请求流程
        
        流程：
        1. 生成色彩方案
        2. 解析颜色信息
        3. 使用程序化生成器生成家具并应用颜色，或在场景中查找已有对象
        
        Args:
            user_request: 用户请求
            scene_path: 输入场景文件路径
            output_path: 输出场景文件路径（可选）
            use_procedural_generation: 是否使用程序化生成（默认 True）
            
        Returns:
            输出场景文件路径
        """
        print("="*60)
        print("Infinigen 智能体开始处理请求")
        print("="*60)
        
        # 步骤1: 生成色彩方案
        color_scheme = self.generate_color_scheme(user_request)
        
        # 步骤2: 解析颜色
        colors = self.parse_colors(color_scheme)
        
        if not colors:
            raise Exception("未能解析出有效的颜色信息")
        
        # 加载场景
        from src.scene_color_applier import SceneColorApplier
        applier = SceneColorApplier(scene_path)
        
        # 步骤3: 使用程序化生成器生成家具并应用颜色，或在场景中查找已有对象
        if use_procedural_generation:
            print("\n" + "="*60)
            print("步骤3: 使用程序化生成器生成家具并应用颜色")
            print("="*60)
            
            # 初始化程序化生成器
            generator = ProceduralFurnitureGenerator(
                factory_seed=np.random.randint(1, 1e9),
                coarse=False
            )
            
            # 分类家具：支持程序化生成 vs 不支持
            procedural_supported = []
            procedural_unsupported = []
            
            for color in colors:
                furniture_type = color.furniture_type.lower()
                
                # 检查是否支持程序化生成
                if generator.is_furniture_type_supported(furniture_type):
                    procedural_supported.append(color)
                else:
                    procedural_unsupported.append(color)
            
            # 对支持程序化生成的家具进行生成
            if procedural_supported:
                print(f"\n使用程序化生成器生成 {len(procedural_supported)} 个家具类型:")
                for color in procedural_supported:
                    furniture_type = color.furniture_type.lower()
                    
                    # 生成家具（默认位置在原点，可以根据需要调整）
                    # 在生成时直接指定颜色
                    obj = generator.generate_furniture(
                        furniture_type=furniture_type,
                        location=(0, 0, 0),  # 可以根据场景调整位置
                        color=color.rgb if color.rgb else None  # 生成时直接应用颜色
                    )
                    
                    if obj:
                        # 如果生成时已经应用了颜色（通过color参数），则不需要再次应用
                        if color.rgb:
                            # 颜色已在生成时应用（通过generate_furniture的color参数）
                            print(f"  ✓ {furniture_type}: 已生成（生成时已应用颜色 {color.rgb}）")
                        else:
                            # 如果没有RGB值，尝试应用颜色名称
                            applier.apply_color_to_object(obj, color)
                            print(f"  ✓ {furniture_type}: 已生成并应用颜色")
                    else:
                        print(f"  ✗ {furniture_type}: 生成失败")
            
            # 对于不支持程序化生成的家具，在场景中查找已有对象
            if procedural_unsupported:
                print(f"\n在场景中查找 {len(procedural_unsupported)} 个已有对象并应用颜色:")
                for color in procedural_unsupported:
                    objects = applier.find_objects_by_name([color.furniture_type])
                    if objects:
                        for obj in objects:
                            applier.apply_color_to_object(obj, color)
                        print(f"  ✓ {color.furniture_type}: 找到 {len(objects)} 个对象并应用颜色")
                    else:
                        print(f"  ⚠ {color.furniture_type}: 未找到匹配的对象（不支持程序化生成且场景中不存在）")
        else:
            # 不使用程序化生成，只在场景中查找已有对象
            print("\n" + "="*60)
            print("步骤3: 在场景中查找已有家具并应用颜色")
            print("="*60)
            applier.apply_colors_to_scene(colors)
        
        # 保存最终场景
        if output_path is None:
            output_path = scene_path.replace('.blend', '_colored.blend')
        
        applier.save_scene(output_path)
        
        print("="*60)
        print("✓ 处理完成！")
        print(f"输出文件: {output_path}")
        print("="*60)
        
        return output_path
    
    def render_scene_image(
        self,
        scene_path: str,
        output_image: str,
        resolution: Optional[tuple] = None
    ) -> str:
        """
        渲染场景图片
        
        Args:
            scene_path: 场景文件路径
            output_image: 输出图片路径
            resolution: 分辨率 (width, height)，默认使用场景设置
            
        Returns:
            输出图片路径
        """
        print(f"\n正在渲染图片...")
        print(f"场景: {scene_path}")
        print(f"输出: {output_image}")
        
        self.scene_renderer = SceneRenderer(scene_path)
        output_path = self.scene_renderer.render_image(
            output_path=output_image,
            resolution=resolution
        )
        
        print(f"✓ 图片已保存: {output_path}")
        return output_path
    
    def process_request_with_render(
        self,
        user_request: str,
        scene_path: str,
        output_path: Optional[str] = None,
        render_image: bool = True,
        resolution: Optional[tuple] = None,
        use_procedural_generation: bool = True
    ) -> dict:
        """
        处理请求并渲染图片
        
        Args:
            user_request: 用户请求
            scene_path: 输入场景文件路径
            output_path: 输出场景文件路径（可选）
            render_image: 是否渲染图片
            resolution: 分辨率 (width, height)
            use_procedural_generation: 是否使用程序化生成
            
        Returns:
            包含输出路径的字典
        """
        # 步骤1-3: 处理颜色
        colored_scene = self.process_request(
            user_request, 
            scene_path, 
            output_path,
            use_procedural_generation=use_procedural_generation
        )
        
        results = {
            "colored_scene": colored_scene
        }
        
        # 步骤4: 渲染图片
        if render_image:
            output_dir = Path(colored_scene).parent
            image_path = output_dir / "rendered_image.png"
            results["image"] = self.render_scene_image(
                scene_path=colored_scene,
                output_image=str(image_path),
                resolution=resolution
            )
        
        return results
    
    def generate_scene_from_request(
        self,
        user_request: str,
        output_folder: str,
        seed: Optional[int] = None,
        gin_configs: Optional[List[str]] = None,
        gin_overrides: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> Path:
        """
        根据用户请求生成场景
        
        Args:
            user_request: 用户请求，如 "生成一个北欧风的卧室"
            output_folder: 输出文件夹路径
            seed: 随机种子（如果为None，则随机生成）
            gin_configs: gin 配置文件列表（默认使用 fast_solve.gin singleroom.gin）
            gin_overrides: gin 参数覆盖列表
            timeout: 超时时间（秒）
            
        Returns:
            生成的场景文件路径
        """
        if not self.scene_generator:
            raise RuntimeError("场景生成器未初始化，无法自动生成场景")
        
        # 如果seed为None，随机生成
        # 注意：Infinigen会将seed字符串作为十六进制解析（如果可能）
        # 使用较小的seed值（1-10000），因为较小的seed通常生成更简单的场景，速度更快
        import random
        if seed is None:
            # 生成0到10000之间的随机整数（较小的seed值，通常生成更快的场景）
            max_seed = 10000
            seed_int = random.randint(0, max_seed)
            # 直接转换为8位十六进制字符串（包含字母），这样：
            # 1. 解析后的值就是seed_int，不会超过max_seed
            # 2. 包含字母，明确表示这是十六进制格式
            seed = format(seed_int, '08x')  # 例如: "00002710" (10000的十六进制)
            print(f"ℹ 未指定seed，使用随机seed: {seed} (解析值: {seed_int})")
        
        # 检测房间类型
        room_type = detect_room_type(user_request)
        
        # 默认使用超快配置（ultra_fast_solve.gin 比 fast_solve.gin 更快）
        if gin_configs is None:
            gin_configs = ["ultra_fast_solve.gin", "singleroom.gin"]
        
        # 构建 gin_overrides（如果未提供）
        if gin_overrides is None:
            gin_overrides = ["compose_indoors.terrain_enabled=False"]
            
            # 如果检测到房间类型，添加房间限制
            # 注意：使用官方文档中的格式，方括号和引号需要转义
            # 格式：restrict_solving.restrict_parent_rooms=\[\"RoomType\"\]
            # 在 Python 字符串中：\\[ 表示 shell 中的 \[，\\" 表示 shell 中的 \"
            if room_type:
                gin_overrides.append(f'restrict_solving.restrict_parent_rooms=\\[\\"{room_type}\\"\\]')
                print(f"✓ 检测到房间类型: {room_type}")
        
        print("="*60)
        print("开始生成场景")
        print("="*60)
        print(f"用户请求: {user_request}")
        if room_type:
            print(f"检测到的房间类型: {room_type}")
        print(f"输出文件夹: {output_folder}")
        print(f"种子: {seed}")
        print(f"Gin 配置: {gin_configs}")
        print(f"Gin 覆盖: {gin_overrides}")
        print("\n提示: 场景生成通常需要 5-15 分钟，请耐心等待...")
        print("     生成过程中会显示详细进度信息")
        print("="*60)
        
        scene_file = self.scene_generator.generate_scene(
            output_folder=output_folder,
            seed=seed,
            task="coarse",
            gin_configs=gin_configs,
            gin_overrides=gin_overrides,
            timeout=timeout
        )
        
        print("\n" + "="*60)
        print(f"✓ 场景生成成功: {scene_file}")
        print("="*60)
        
        # 如果用户请求包含颜色信息，在生成后立即应用颜色
        # 这样可以和原生命令生成流程无缝集成
        if user_request and self._should_apply_colors(user_request):
            print("\n" + "="*60)
            print("检测到颜色需求，正在应用颜色...")
            print("="*60)
            
            try:
                # 创建颜色应用回调函数
                def apply_colors_callback(scene_path: Path) -> str:
                    """在场景生成后立即应用颜色的回调函数"""
                    colored_scene = self.process_request(
                        user_request=user_request,
                        scene_path=str(scene_path),
                        output_path=None,  # 使用默认命名
                        import_missing_assets=False,  # 场景已生成，不需要导入
                        use_procedural_generation=False  # 场景已生成，不需要程序化生成
                    )
                    return colored_scene
                
                # 使用回调在生成后立即应用颜色
                colored_scene = self.scene_generator.generate_scene(
                    output_folder=output_folder,
                    seed=seed,
                    task="coarse",
                    gin_configs=gin_configs,
                    gin_overrides=gin_overrides,
                    timeout=timeout,
                    apply_colors_callback=apply_colors_callback
                )
                
                print("\n" + "="*60)
                print(f"✓ 场景生成并应用颜色成功: {colored_scene}")
                print("="*60)
                return colored_scene
                
            except Exception as e:
                print(f"\n⚠ 应用颜色时出错: {e}")
                import traceback
                traceback.print_exc()
                print("继续使用原始场景文件")
                return scene_file
        
        return scene_file
    
    def _should_apply_colors(self, user_request: str) -> bool:
        """
        判断用户请求是否包含颜色需求
        
        Args:
            user_request: 用户请求
            
        Returns:
            是否需要应用颜色
        """
        # 简单的关键词检测
        color_keywords = [
            "颜色", "色彩", "色", "color", "colour",
            "红色", "蓝色", "绿色", "黄色", "白色", "黑色",
            "red", "blue", "green", "yellow", "white", "black",
            "北欧", "现代", "风格", "style"
        ]
        
        user_request_lower = user_request.lower()
        return any(keyword in user_request_lower for keyword in color_keywords)
    
    def process_request_with_auto_generate(
        self,
        user_request: str,
        output_folder: str,
        seed: int = 0,
        gin_configs: Optional[List[str]] = None,
        gin_overrides: Optional[List[str]] = None,
        generate_timeout: Optional[int] = None,
        render_image: bool = True,
        resolution: Optional[tuple] = None
    ) -> dict:
        """
        完整流程：从用户输入自动生成场景、应用颜色、渲染图片
        
        Args:
            user_request: 用户请求，如 "生成一个北欧风的卧室"
            output_folder: 输出文件夹路径
            seed: 随机种子
            gin_configs: gin 配置文件列表（默认使用 fast_solve.gin singleroom.gin）
            gin_overrides: gin 参数覆盖列表
            generate_timeout: 场景生成超时时间（秒）
            render_image: 是否渲染图片
            resolution: 分辨率 (width, height)
            
        Returns:
            包含所有输出路径的字典
        """
        print("="*60)
        print("Infinigen 智能体 - 完整自动流程")
        print("="*60)
        
        # 步骤1: 生成场景
        scene_file = self.generate_scene_from_request(
            user_request=user_request,
            output_folder=output_folder,
            seed=seed,
            gin_configs=gin_configs,
            gin_overrides=gin_overrides,
            timeout=generate_timeout
        )
        
        # 步骤2-3: 应用颜色并渲染
        results = self.process_request_with_render(
            user_request=user_request,
            scene_path=str(scene_file),
            output_path=None,  # 使用默认命名
            render_image=render_image,
            resolution=resolution
        )
        
        results["generated_scene"] = scene_file
        
        print("="*60)
        print("✓ 完整流程执行成功！")
        print("="*60)
        print(f"生成的场景: {results['generated_scene']}")
        print(f"带颜色的场景: {results['colored_scene']}")
        if 'image' in results:
            print(f"渲染的图片: {results['image']}")
        
        return results


if __name__ == "__main__":
    # 测试示例
    agent = InfinigenAgent()
    
    # 测试流程
    test_request = "生成一个北欧风的卧室"
    test_scene = "../outputs/hello_room/coarse/scene.blend"
    
    if Path(test_scene).exists():
        try:
            output = agent.process_request(
                user_request=test_request,
                scene_path=test_scene
            )
            print(f"\n成功！输出文件: {output}")
        except Exception as e:
            print(f"\n错误: {e}")
    else:
        print(f"场景文件不存在: {test_scene}")

