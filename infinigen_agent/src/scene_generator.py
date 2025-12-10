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
        
        # 查找 shell 脚本路径
        script_path = Path(__file__).parent.parent / "scripts" / "generate_scene.sh"
        self.shell_script = script_path if script_path.exists() else None
    
    def generate_scene(
        self,
        output_folder: str,
        seed: Optional[int] = None,
        task: str | list[str] = "coarse",
        gin_configs: Optional[list] = None,
        gin_overrides: Optional[list] = None,
        timeout: Optional[int] = None,
        use_shell_script: bool = False,
        auto_rename: bool = True,
        apply_colors_callback: Optional[callable] = None
    ) -> Path:
        """
        生成场景
        
        Args:
            output_folder: 输出文件夹路径
            seed: 随机种子（如果为None，则随机生成）
            task: 任务类型，可以是：
                - 单个任务: 'coarse' 或 'render'
                - 多个任务: ['coarse', 'render'] 或 'coarse render'（一步完成生成和渲染）
            gin_configs: gin 配置文件列表，如 ['base', 'disable/no_objects']
            gin_overrides: gin 参数覆盖列表，如 ['compose_indoors.terrain_enabled=False']
            timeout: 超时时间（秒），None 表示不设置超时
            use_shell_script: 是否使用 shell 脚本方式
            auto_rename: 如果输出文件夹已存在，是否自动重命名（添加时间戳），默认 True
            
        Returns:
            生成的场景文件路径（.blend 文件）
        """
        output_path = Path(output_folder).resolve()
        
        # 检查输出文件夹是否已存在
        if output_path.exists() and output_path.is_dir():
            # 检查是否包含场景文件（说明之前已经生成过）
            existing_scene = self._find_scene_file(output_path)
            if existing_scene and auto_rename:
                # 自动重命名，添加时间戳
                import time
                timestamp = int(time.time())
                new_name = f"{output_path.name}_{timestamp}"
                output_path = output_path.parent / new_name
                logger.warning(
                    f"输出文件夹已存在且包含场景文件，自动重命名为: {output_path.name}"
                )
            elif existing_scene and not auto_rename:
                logger.warning(
                    f"警告: 输出文件夹已存在且包含场景文件: {existing_scene}"
                    f"\n将覆盖已有文件。如需避免覆盖，请设置 auto_rename=True"
                )
        
        # 确保输出目录存在（包括所有父目录）
        # 重要：必须在调用 Infinigen 之前创建，因为 Infinigen 内部会尝试保存文件
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 确保目录确实存在（双重检查）
        if not output_path.exists():
            raise RuntimeError(f"无法创建输出目录: {output_path}")
        
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
            logger.info(f"未指定seed，使用随机seed: {seed} (解析值: {seed_int})")
        
        # 默认 gin 配置（匹配官方 hello_room 配置）
        # 注意：根据 generate_indoors.py 第 518 行，官方会自动加载 base_indoors.gin
        # 如果 gin_configs 为空，使用官方 hello_room 推荐配置
        if gin_configs is None:
            gin_configs = ['fast_solve.gin', 'singleroom.gin']
        
        # 处理 task 参数：支持单个任务或多个任务
        # Infinigen 原生支持 -t coarse render 一次完成生成和渲染
        if isinstance(task, str):
            task_list = [task]
        else:
            task_list = task
        
        # 如果使用 shell 脚本方式
        if use_shell_script and self.shell_script:
            return self._generate_scene_via_shell_script(
                output_path, seed, task_list, gin_configs, timeout, apply_colors_callback
            )
        
        # 构建 shell 命令字符串（与 Infinigen 原生脚本一致）
        # 原生脚本使用: python -m infinigen_examples.generate_indoors --output_folder ... -s ... -g ... -t ...
        # 支持多个任务: -t coarse render（一步完成生成和渲染）
        # 为了和原生结果完全一致，使用 shell 命令方式执行
        cmd_parts = [
            sys.executable,
            '-m', 'infinigen_examples.generate_indoors',
            '--output_folder', str(output_path),
            '-s', str(seed),
            '-t'
        ]
        # 添加所有任务（支持多个任务）
        cmd_parts.extend(task_list)
        
        # 添加 gin 配置（使用 -g 参数，多个配置用空格分隔，与原生脚本一致）
        if gin_configs:
            for config in gin_configs:
                cmd_parts.extend(['-g', config])
        
        # 添加 gin 参数覆盖（使用 -p 参数，多个覆盖用空格分隔，与原生脚本一致）
        if gin_overrides:
            cmd_parts.append('-p')
            for override in gin_overrides:
                # gin_overrides 中的参数可能已经包含转义（如列表参数）
                # 直接添加，不要再次转义
                cmd_parts.append(override)
        
        # 构建完整的 shell 命令字符串（与原生脚本执行方式一致）
        # 注意：使用 shell=True 确保和原生脚本的执行环境一致
        # gin_overrides 中的参数格式：restrict_solving.restrict_parent_rooms=\[\"RoomType\"\]
        # 在 shell 中，\[ 会被解释为 [，\" 会被解释为 "，所以最终传递给 gin 的是 ["RoomType"]
        # 关键：直接使用 gin_overrides 中的格式，不要额外转义或包裹
        # 官方命令格式就是这样的，shell 会正确解释
        shell_cmd = ' '.join(str(part) for part in cmd_parts)
        
        logger.info(f"开始生成场景...")
        logger.info(f"输出文件夹: {output_path}")
        logger.info(f"种子: {seed}, 任务: {task_list}")
        logger.info(f"Gin 配置: {gin_configs}")
        if gin_overrides:
            logger.info(f"Gin 覆盖: {gin_overrides}")
        if len(task_list) > 1:
            logger.info(f"⚠ 将一次完成多个任务: {', '.join(task_list)}")
        logger.info(f"命令（与原生脚本一致）: {shell_cmd}")
        
        # 切换到 Infinigen 根目录执行 shell 命令（与原生脚本一致）
        try:
            print("\n" + "="*60)
            print("⚠ 场景生成需要几分钟到十几分钟，请耐心等待...")
            print("="*60)
            print("正在运行命令（与 Infinigen 原生脚本一致）:")
            print(f"  cd {self.infinigen_root}")
            print(f"  {shell_cmd}")
            print("="*60)
            print(f"输出文件夹: {output_path}")
            print("="*60 + "\n")
            
            # 使用 shell=True 执行命令，确保和原生脚本的执行环境完全一致
            # 这样结果才会和原生脚本生成的结果一样
            if timeout:
                result = subprocess.run(
                    shell_cmd,
                    shell=True,
                    cwd=str(self.infinigen_root),
                    timeout=timeout,
                    # 不捕获输出，让输出实时显示
                    check=True
                )
            else:
                result = subprocess.run(
                    shell_cmd,
                    shell=True,
                    cwd=str(self.infinigen_root),
                    # 不捕获输出，让输出实时显示
                    check=True
                )
            
            logger.info("场景生成成功")
            
            # 等待场景文件生成（如果命令完成但文件还没生成，等待一段时间）
            import time
            max_wait_time = 60  # 最多等待60秒
            wait_interval = 2   # 每2秒检查一次
            waited_time = 0
            
            scene_file = None
            while waited_time < max_wait_time:
                scene_file = self._find_scene_file(output_path)
                if scene_file and scene_file.exists():
                    # 检查文件大小，确保文件已完全写入（至少大于1KB）
                    if scene_file.stat().st_size > 1024:
                        logger.info(f"✓ 找到场景文件: {scene_file} (大小: {scene_file.stat().st_size / (1024*1024):.2f} MB)")
                        break
                    else:
                        logger.debug(f"场景文件存在但可能未完全写入，继续等待...")
                else:
                    logger.debug(f"等待场景文件生成... ({waited_time}/{max_wait_time}秒)")
                time.sleep(wait_interval)
                waited_time += wait_interval
            
            if scene_file and scene_file.exists() and scene_file.stat().st_size > 1024:
                logger.info(f"✓ 场景文件已生成并确认: {scene_file}")
                print(f"✓ 场景文件已生成: {scene_file}")
                print(f"  文件大小: {scene_file.stat().st_size / (1024*1024):.2f} MB")
                
                # 如果提供了颜色应用回调，在生成后立即应用颜色
                if apply_colors_callback:
                    try:
                        logger.info("正在应用颜色到场景...")
                        colored_scene = apply_colors_callback(scene_file)
                        if colored_scene and Path(colored_scene).exists():
                            logger.info(f"颜色应用成功: {colored_scene}")
                            return Path(colored_scene)
                        else:
                            logger.warning("颜色应用回调未返回有效路径，使用原始场景文件")
                    except Exception as e:
                        logger.error(f"应用颜色时出错: {e}")
                        logger.warning("继续使用原始场景文件")
                
                print(f"✓ generate_scene 返回: {scene_file}")
                return scene_file
            else:
                if scene_file:
                    file_size = scene_file.stat().st_size if scene_file.exists() else 0
                    logger.warning(f"场景文件存在但可能无效: {scene_file} (大小: {file_size} 字节)")
                    print(f"⚠ 场景文件可能未完全生成: {scene_file} (大小: {file_size} 字节)")
                else:
                    logger.warning("未找到场景文件，但命令执行成功")
                    print(f"⚠ 未找到场景文件，尝试使用输出目录: {output_path}")
                    # 尝试在输出目录中查找场景文件
                    blend_files = list(output_path.rglob("*.blend"))
                    if blend_files:
                        scene_file = blend_files[0]
                        if scene_file.stat().st_size > 1024:
                            print(f"✓ 在输出目录中找到场景文件: {scene_file}")
                            return scene_file
                
                # 即使没找到文件，也返回输出路径，让调用者决定如何处理
                print(f"⚠ generate_scene 返回输出目录: {output_path}")
                return output_path
            
        except subprocess.TimeoutExpired:
            logger.error(f"场景生成超时（{timeout}秒）")
            raise TimeoutError(f"场景生成超时（{timeout}秒）")
        except subprocess.CalledProcessError as e:
            # 如果捕获了输出，尝试获取错误信息
            error_msg = getattr(e, 'stderr', '') or getattr(e, 'stdout', '') or str(e)
            logger.error(f"场景生成失败: {e}")
            if error_msg:
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
    
    def _generate_scene_via_shell_script(
        self,
        output_path: Path,
        seed: str,
        task: str | list[str],
        gin_configs: list,
        timeout: Optional[int],
        apply_colors_callback: Optional[callable] = None
    ) -> Path:
        """
        通过 shell 脚本生成场景
        
        Args:
            output_path: 输出路径
            seed: 种子
            task: 任务类型
            gin_configs: gin 配置列表
            timeout: 超时时间
            
        Returns:
            场景文件路径
        """
        if not self.shell_script:
            raise ValueError("Shell 脚本不存在，无法使用 shell 脚本方式")
        
        # 处理 task 参数
        if isinstance(task, str):
            task_list = [task]
        else:
            task_list = task
        
        # 构建 shell 脚本命令
        cmd_parts = [str(self.shell_script)]
        cmd_parts.extend(['--output-folder', str(output_path)])
        cmd_parts.extend(['-s', str(seed)])
        cmd_parts.extend(['-t'] + task_list)  # 支持多个任务
        
        # 添加 gin 配置
        for config in gin_configs:
            cmd_parts.extend(['-g', config])
        
        if timeout:
            cmd_parts.extend(['--timeout', str(timeout)])
        
        shell_cmd = ' '.join(f'"{part}"' if ' ' in str(part) else str(part) for part in cmd_parts)
        
        logger.info(f"使用 Shell 脚本生成场景...")
        logger.info(f"Shell 脚本: {self.shell_script}")
        logger.info(f"命令: {shell_cmd}")
        
        try:
            print("\n" + "="*60)
            print("⚠ 使用 Shell 脚本生成场景...")
            print("="*60)
            print(f"Shell 脚本: {self.shell_script}")
            print(f"命令: {shell_cmd}")
            print("="*60 + "\n")
            
            if timeout:
                result = subprocess.run(
                    shell_cmd,
                    shell=True,
                    timeout=timeout,
                    check=True
                )
            else:
                result = subprocess.run(
                    shell_cmd,
                    shell=True,
                    check=True
                )
            
            logger.info("场景生成成功（通过 Shell 脚本）")
            
            # 查找生成的场景文件
            scene_file = self._find_scene_file(output_path)
            if scene_file:
                logger.info(f"找到场景文件: {scene_file}")
                
                # 如果提供了颜色应用回调，在生成后立即应用颜色
                if apply_colors_callback:
                    try:
                        logger.info("正在应用颜色到场景...")
                        colored_scene = apply_colors_callback(scene_file)
                        if colored_scene and Path(colored_scene).exists():
                            logger.info(f"颜色应用成功: {colored_scene}")
                            return Path(colored_scene)
                        else:
                            logger.warning("颜色应用回调未返回有效路径，使用原始场景文件")
                    except Exception as e:
                        logger.error(f"应用颜色时出错: {e}")
                        logger.warning("继续使用原始场景文件")
                
                return scene_file
            else:
                logger.warning("未找到场景文件，但命令执行成功")
                return output_path
                
        except subprocess.TimeoutExpired:
            logger.error(f"场景生成超时（{timeout}秒）")
            raise TimeoutError(f"场景生成超时（{timeout}秒）")
        except subprocess.CalledProcessError as e:
            error_msg = getattr(e, 'stderr', '') or getattr(e, 'stdout', '') or str(e)
            logger.error(f"场景生成失败（Shell 脚本）: {error_msg}")
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
        timeout: Optional[int] = None,
        one_step: bool = True
    ) -> dict:
        """
        生成场景并渲染
        
        Args:
            output_folder: 输出文件夹路径
            seed: 随机种子
            gin_configs: gin 配置文件列表
            render_output_folder: 渲染输出文件夹，如果为 None 则在场景文件夹下创建 frames 文件夹
            timeout: 超时时间（秒）
            one_step: 是否使用一步完成（使用 -t coarse render），默认 True
                     如果 False，则分两步执行（先 coarse，再 render）
            
        Returns:
            包含场景文件路径和渲染输出路径的字典
        """
        if one_step:
            # 方式1: 一步完成（使用 Infinigen 原生命令，推荐）
            # 使用 -t coarse render 一次完成生成和渲染
            logger.info("使用一步完成方式：-t coarse render")
            scene_file = self.generate_scene(
                output_folder=output_folder,
                seed=seed,
                task=["coarse", "render"],  # 多个任务一次完成
                gin_configs=gin_configs,
                timeout=timeout
            )
            
            # 查找渲染输出（通常在 output_folder/coarse/frames 或 output_folder/frames）
            render_output = Path(output_folder) / "coarse" / "frames"
            if not render_output.exists():
                render_output = Path(output_folder) / "frames"
            
            return {
                "scene_file": scene_file,
                "render_output": render_output
            }
        else:
            # 方式2: 分两步执行（兼容旧方式）
            logger.info("使用分步方式：先 coarse，再 render")
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
