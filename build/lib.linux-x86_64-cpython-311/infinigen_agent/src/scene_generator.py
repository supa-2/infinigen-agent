"""
场景生成器模块
封装 Infinigen 的场景生成功能
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SceneGenerator:
    """场景生成器类，用于从零生成 Infinigen 场景"""
    
    def __init__(self, infinigen_root: Optional[str] = None):
        """
        初始化场景生成器
        
        Args:
            infinigen_root: Infinigen 根目录路径，默认为 ../infinigen
        """
        if infinigen_root is None:
            # 默认假设 infinigen_agent 在 infinigen 目录下
            current_dir = Path(__file__).parent.parent
            if current_dir.name == 'infinigen_agent':
                infinigen_root = current_dir.parent
            else:
                # 如果不在 infinigen 目录下，尝试查找
                infinigen_root = current_dir.parent / 'infinigen'
                if not infinigen_root.exists():
                    infinigen_root = Path('/home/ubuntu/infinigen')  # 默认路径
        
        self.infinigen_root = Path(infinigen_root).resolve()
        
        if not self.infinigen_root.exists():
            raise ValueError(f"Infinigen 根目录不存在: {self.infinigen_root}")
        
        logger.info(f"场景生成器初始化，Infinigen 根目录: {self.infinigen_root}")
    
    def generate_scene(
        self,
        output_folder: str,
        seed: int = 0,
        task: str = "coarse",
        gin_configs: Optional[list] = None,
        timeout: Optional[int] = None
    ) -> Path:
        """
        生成场景
        
        Args:
            output_folder: 输出文件夹路径
            seed: 随机种子
            task: 任务类型，'coarse' 或 'render'
            gin_configs: gin 配置文件列表，如 ['base', 'disable/no_objects']
            timeout: 超时时间（秒），None 表示不设置超时
            
        Returns:
            生成的场景文件路径（.blend 文件）
        """
        output_path = Path(output_folder).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 默认 gin 配置
        # 注意：如果遇到 terrain 编译错误，可以尝试使用 'disable/terrain' 配置
        if gin_configs is None:
            gin_configs = ['base', 'disable/no_objects']
        
        # 构建命令
        cmd = [
            sys.executable,
            '-m', 'infinigen_examples.generate_indoors',
            '--output_folder', str(output_path),
            '-s', str(seed),  # 使用 -s 而不是 --seed
            '-t', task  # 使用 -t 而不是 --task
        ]
        
        # 添加 gin 配置（使用 -g 参数，多个配置用空格分隔）
        if gin_configs:
            cmd.extend(['-g'] + gin_configs)
        
        logger.info(f"开始生成场景...")
        logger.info(f"输出文件夹: {output_path}")
        logger.info(f"种子: {seed}, 任务: {task}")
        logger.info(f"命令: {' '.join(cmd)}")
        
        # 切换到 Infinigen 根目录执行
        try:
            if timeout:
                result = subprocess.run(
                    cmd,
                    cwd=str(self.infinigen_root),
                    timeout=timeout,
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                result = subprocess.run(
                    cmd,
                    cwd=str(self.infinigen_root),
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            logger.info("场景生成成功")
            
            # 查找生成的场景文件
            scene_file = self._find_scene_file(output_path)
            if scene_file:
                logger.info(f"找到场景文件: {scene_file}")
                return scene_file
            else:
                logger.warning("未找到场景文件，但命令执行成功")
                return output_path
            
        except subprocess.TimeoutExpired:
            logger.error(f"场景生成超时（{timeout}秒）")
            raise TimeoutError(f"场景生成超时（{timeout}秒）")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"场景生成失败: {e}")
            logger.error(f"错误输出: {error_msg}")
            
            # 检查是否是 terrain 相关错误
            if "waterbody.so" in error_msg or "terrain" in error_msg.lower():
                logger.error("\n⚠ 检测到 terrain 相关错误")
                if "landlab" in error_msg or "No module named 'landlab'" in error_msg:
                    logger.error("提示: 缺少 terrain 依赖模块 'landlab'")
                    logger.error("解决方案:")
                    logger.error("  安装 terrain 依赖:")
                    logger.error("    cd /home/ubuntu/infinigen")
                    logger.error("    conda activate infinigen")
                    logger.error("    pip install .[terrain]")
                elif "waterbody.so" in error_msg:
                    logger.error("提示: Infinigen 的 terrain 模块需要编译 C++ 库")
                    logger.error("解决方案:")
                    logger.error("  1. 编译 terrain 模块: cd infinigen && bash scripts/install/compile_terrain.sh")
                    logger.error("  2. 安装 terrain 依赖: pip install .[terrain]")
                else:
                    logger.error("提示: Infinigen 的 terrain 模块配置问题")
                    logger.error("解决方案:")
                    logger.error("  1. 安装 terrain 依赖: cd infinigen && pip install .[terrain]")
                    logger.error("  2. 或使用已有的场景文件而不是自动生成")
            
            raise RuntimeError(f"场景生成失败: {error_msg}")
    
    def _find_scene_file(self, output_folder: Path) -> Optional[Path]:
        """
        查找生成的场景文件
        
        Args:
            output_folder: 输出文件夹
            
        Returns:
            场景文件路径，如果未找到则返回 None
        """
        # 常见的场景文件位置
        possible_paths = [
            output_folder / "scene.blend",
            output_folder / "coarse" / "scene.blend",
            output_folder / "outputs" / "scene.blend",
        ]
        
        # 递归搜索 .blend 文件
        for blend_file in output_folder.rglob("*.blend"):
            if blend_file.is_file():
                return blend_file
        
        return None
    
    def generate_and_render(
        self,
        output_folder: str,
        seed: int = 0,
        gin_configs: Optional[list] = None,
        render_output_folder: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> dict:
        """
        生成场景并渲染
        
        Args:
            output_folder: 输出文件夹路径
            seed: 随机种子
            gin_configs: gin 配置文件列表
            render_output_folder: 渲染输出文件夹，如果为 None 则在场景文件夹下创建 frames 文件夹
            timeout: 超时时间（秒）
            
        Returns:
            包含场景文件路径和渲染输出路径的字典
        """
        # 步骤1: 生成场景（coarse 任务）
        scene_file = self.generate_scene(
            output_folder=output_folder,
            seed=seed,
            task="coarse",
            gin_configs=gin_configs,
            timeout=timeout
        )
        
        # 步骤2: 渲染场景
        if render_output_folder is None:
            render_output_folder = str(Path(output_folder) / "frames")
        
        render_scene_file = self.generate_scene(
            output_folder=render_output_folder,
            seed=seed,
            task="render",
            gin_configs=gin_configs,
            timeout=timeout
        )
        
        return {
            "scene_file": scene_file,
            "render_output": Path(render_output_folder)
        }


if __name__ == "__main__":
    # 测试场景生成器
    import logging
    logging.basicConfig(level=logging.INFO)
    
    generator = SceneGenerator()
    
    print("测试场景生成...")
    try:
        result = generator.generate_scene(
            output_folder="/tmp/test_scene",
            seed=0,
            task="coarse",
            timeout=300  # 5分钟超时
        )
        print(f"✓ 场景生成成功: {result}")
    except Exception as e:
        print(f"✗ 场景生成失败: {e}")
