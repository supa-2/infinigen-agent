"""
主智能体系统
整合 vLLM、颜色解析和场景修改功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vllm_client import VLLMClient
from src.color_parser import ColorParser
from src.scene_color_applier import SceneColorApplier
from src.scene_renderer import SceneRenderer
from src.scene_generator import SceneGenerator
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
        output_path: Optional[str] = None
    ) -> str:
        """
        处理完整的用户请求流程
        
        Args:
            user_request: 用户请求
            scene_path: 输入场景文件路径
            output_path: 输出场景文件路径（可选）
            
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
        
        # 步骤3: 应用颜色到场景
        output_path = self.apply_colors_to_scene(scene_path, colors, output_path)
        
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
    
    def render_scene_video(
        self,
        scene_path: str,
        output_folder: str,
        num_frames: int = 60,
        fps: int = 24,
        resolution: Optional[tuple] = None
    ) -> str:
        """
        渲染场景视频
        
        Args:
            scene_path: 场景文件路径
            output_folder: 输出文件夹
            num_frames: 帧数
            fps: 帧率
            resolution: 分辨率
            
        Returns:
            输出视频路径
        """
        print(f"\n正在渲染视频...")
        print(f"场景: {scene_path}")
        print(f"输出文件夹: {output_folder}")
        print(f"帧数: {num_frames}, 帧率: {fps} fps")
        
        self.scene_renderer = SceneRenderer(scene_path)
        output_path = self.scene_renderer.render_and_create_video(
            output_folder=output_folder,
            num_frames=num_frames,
            fps=fps,
            resolution=resolution
        )
        
        print(f"✓ 视频已保存: {output_path}")
        return output_path
    
    def process_request_with_render(
        self,
        user_request: str,
        scene_path: str,
        output_path: Optional[str] = None,
        render_image: bool = True,
        render_video: bool = False,
        video_frames: int = 60,
        video_fps: int = 24,
        resolution: Optional[tuple] = None
    ) -> dict:
        """
        处理请求并渲染图片/视频
        
        Args:
            user_request: 用户请求
            scene_path: 输入场景文件路径
            output_path: 输出场景文件路径（可选）
            render_image: 是否渲染图片
            render_video: 是否渲染视频
            video_frames: 视频帧数
            video_fps: 视频帧率
            resolution: 分辨率 (width, height)
            
        Returns:
            包含输出路径的字典
        """
        # 步骤1-3: 处理颜色（原有流程）
        colored_scene = self.process_request(user_request, scene_path, output_path)
        
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
        
        # 步骤5: 渲染视频
        if render_video:
            output_dir = Path(colored_scene).parent
            video_folder = output_dir / "video_output"
            results["video"] = self.render_scene_video(
                scene_path=colored_scene,
                output_folder=str(video_folder),
                num_frames=video_frames,
                fps=video_fps,
                resolution=resolution
            )
        
        return results
    
    def generate_scene_from_request(
        self,
        user_request: str,
        output_folder: str,
        seed: int = 0,
        gin_configs: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> Path:
        """
        根据用户请求生成场景
        
        Args:
            user_request: 用户请求，如 "生成一个北欧风的卧室"
            output_folder: 输出文件夹路径
            seed: 随机种子
            gin_configs: gin 配置文件列表
            timeout: 超时时间（秒）
            
        Returns:
            生成的场景文件路径
        """
        if not self.scene_generator:
            raise RuntimeError("场景生成器未初始化，无法自动生成场景")
        
        print("="*60)
        print("开始生成场景")
        print("="*60)
        print(f"用户请求: {user_request}")
        print(f"输出文件夹: {output_folder}")
        print(f"种子: {seed}")
        
        scene_file = self.scene_generator.generate_scene(
            output_folder=output_folder,
            seed=seed,
            task="coarse",
            gin_configs=gin_configs,
            timeout=timeout
        )
        
        print(f"✓ 场景生成成功: {scene_file}")
        return scene_file
    
    def process_request_with_auto_generate(
        self,
        user_request: str,
        output_folder: str,
        seed: int = 0,
        gin_configs: Optional[List[str]] = None,
        generate_timeout: Optional[int] = None,
        render_image: bool = True,
        render_video: bool = False,
        video_frames: int = 60,
        video_fps: int = 24,
        resolution: Optional[tuple] = None
    ) -> dict:
        """
        完整流程：从用户输入自动生成场景、应用颜色、渲染图片/视频
        
        Args:
            user_request: 用户请求，如 "生成一个北欧风的卧室"
            output_folder: 输出文件夹路径
            seed: 随机种子
            gin_configs: gin 配置文件列表
            generate_timeout: 场景生成超时时间（秒）
            render_image: 是否渲染图片
            render_video: 是否渲染视频
            video_frames: 视频帧数
            video_fps: 视频帧率
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
            timeout=generate_timeout
        )
        
        # 步骤2-4: 应用颜色并渲染（复用现有方法）
        results = self.process_request_with_render(
            user_request=user_request,
            scene_path=str(scene_file),
            output_path=None,  # 使用默认命名
            render_image=render_image,
            render_video=render_video,
            video_frames=video_frames,
            video_fps=video_fps,
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
        if 'video' in results:
            print(f"渲染的视频: {results['video']}")
        
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

