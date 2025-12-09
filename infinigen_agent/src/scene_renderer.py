"""
场景渲染模块
用于渲染场景图片和视频
"""
import bpy
import subprocess
from pathlib import Path
from typing import Optional, List
import sys
import os

# 添加 infinigen 路径
infinigen_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(infinigen_root))

from infinigen.core.rendering.render import render_image
from infinigen.core.placement import camera as cam_util


class SceneRenderer:
    """场景渲染器"""
    
    def __init__(self, scene_path: Optional[str] = None):
        """
        初始化场景渲染器
        
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
    
    def get_cameras(self) -> List[bpy.types.Object]:
        """
        获取场景中的所有相机
        
        Returns:
            相机对象列表
        """
        cameras = []
        camera_rig_children = []  # 相机rig的子相机（通常是室内相机）
        direct_cameras = []  # 直接相机对象
        
        for obj in bpy.context.scene.objects:
            if obj.type == 'CAMERA':
                direct_cameras.append(obj)
            # 也查找相机rig
            elif 'camera' in obj.name.lower() or 'cam' in obj.name.lower():
                # 检查是否有子对象是相机
                for child in obj.children:
                    if child.type == 'CAMERA':
                        camera_rig_children.append(child)
        
        # 优先使用相机rig的子相机（这些通常是室内相机，由generate_indoors生成）
        if camera_rig_children:
            cameras.extend(camera_rig_children)
            print(f"✓ 找到 {len(camera_rig_children)} 个相机rig子相机（室内相机）")
        
        # 然后添加直接相机对象
        if direct_cameras:
            cameras.extend(direct_cameras)
            if camera_rig_children:
                print(f"  以及 {len(direct_cameras)} 个直接相机对象")
        
        if not cameras:
            # 如果没有找到相机，使用场景默认相机
            if bpy.context.scene.camera:
                cameras.append(bpy.context.scene.camera)
                print("⚠ 使用场景默认相机")
            else:
                print("⚠ 未找到相机，将创建默认相机")
                self.create_default_camera()
                cameras.append(bpy.context.scene.camera)
        
        return cameras
    
    def create_default_camera(self):
        """创建默认相机"""
        # 创建相机
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = "DefaultCamera"
        
        # 设置相机位置（从上方俯视）
        camera.location = (0, 0, 5)
        camera.rotation_euler = (1.5708, 0, 0)  # 90度向下看
        
        # 设置为活动相机
        bpy.context.scene.camera = camera
        print("✓ 已创建默认相机")
    
    def render_image(
        self,
        output_path: str,
        camera: Optional[bpy.types.Object] = None,
        resolution: Optional[tuple] = None,
        passes_to_save: Optional[List[str]] = None
    ) -> str:
        """
        渲染单张图片
        
        Args:
            output_path: 输出图片路径
            camera: 相机对象（如果为None，使用场景默认相机）
            resolution: 分辨率 (width, height)，如果为None使用场景设置
            passes_to_save: 要保存的通道列表，如 ["Image", "Depth"]
            
        Returns:
            输出文件路径
        """
        if camera is None:
            cameras = self.get_cameras()
            if cameras:
                # 优先选择第一个相机（通常是相机rig的子相机，即室内相机）
                camera = cameras[0]
                print(f"✓ 使用相机: {camera.name} (位置: {camera.location})")
            else:
                raise ValueError("未找到相机")
        
        # 设置活动相机
        bpy.context.scene.camera = camera
        if camera is None:
            cameras = self.get_cameras()
            if cameras:
                # 优先选择第一个相机（通常是相机rig的子相机，即室内相机）
                camera = cameras[0]
                print(f"✓ 使用相机: {camera.name} (位置: {camera.location})")
            else:
                raise ValueError("未找到相机")
        
        # 设置分辨率
        if resolution:
            bpy.context.scene.render.resolution_x = resolution[0]
            bpy.context.scene.render.resolution_y = resolution[1]
        
        # 设置输出路径
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建一个干净的frames子目录
        # 使用带时间戳的目录名，确保是全新的，避免reorganize_old_framesfolder解析旧文件
        import time
        import shutil
        
        frames_folder = output_dir / f"frames_render_{int(time.time())}"
        
        # 如果目录已存在，删除它（确保是全新的）
        if frames_folder.exists():
            shutil.rmtree(frames_folder)
        
        frames_folder.mkdir(parents=True, exist_ok=True)
        
        # 设置要保存的通道
        # Infinigen的render_image期望passes_to_save是元组列表: [(viewlayer_pass, socket_name), ...]
        if passes_to_save is None:
            passes_to_save = [("Image", "Image")]
        elif isinstance(passes_to_save, list) and len(passes_to_save) > 0:
            # 如果是字符串列表，转换为元组列表
            if isinstance(passes_to_save[0], str):
                passes_to_save = [(pass_name, pass_name) for pass_name in passes_to_save]
        
        # 调用 Infinigen 的渲染函数
        # 注意：render_image内部会调用reorganize_old_framesfolder，它会尝试解析所有文件名
        # 如果文件名格式不正确（如包含####），会导致解析错误
        # 解决方案：确保frames文件夹是全新的、空的，并且渲染后立即复制文件
        try:
            # 确保frames文件夹是空的（删除可能存在的旧文件）
            for existing_file in frames_folder.glob("*"):
                if existing_file.is_file():
                    existing_file.unlink()
                elif existing_file.is_dir():
                    import shutil
                    shutil.rmtree(existing_file)
            
            render_image(
                camera=camera,
                frames_folder=frames_folder,  # 使用专门的frames文件夹
                passes_to_save=passes_to_save
            )
            
            # 查找渲染的图片文件并复制到输出路径
            # Infinigen会在frames文件夹中创建文件，格式如: Image_0_0_0001_0_0_0.png
            # 或者重新组织后在 camera_0/ 子目录中
            import shutil
            
            # 方法1: 直接在frames文件夹中查找
            rendered_files = list(frames_folder.glob("Image_*.png"))
            
            # 方法2: 在camera子目录中查找（reorganize后）
            if not rendered_files:
                camera_dirs = list(frames_folder.glob("camera_*"))
                for cam_dir in camera_dirs:
                    if cam_dir.is_dir():
                        rendered_files.extend(list(cam_dir.glob("Image_*.png")))
            
            if rendered_files:
                # 使用第一个找到的图片
                shutil.copy2(rendered_files[0], output_path)
                print(f"✓ 图片已渲染并复制到: {output_path}")
                
                # 清理临时frames目录（可选）
                try:
                    shutil.rmtree(frames_folder)
                except Exception:
                    pass  # 忽略清理错误
            else:
                print(f"⚠ 未找到渲染的图片文件")
                print(f"  检查目录: {frames_folder}")
                print(f"  渲染可能已成功，但文件位置不同")
            
            print(f"✓ 图片已渲染到: {output_path}")
            return output_path
        except Exception as e:
            print(f"✗ 渲染失败: {e}")
            raise
    
    def render_multiple_frames(
        self,
        output_folder: str,
        num_frames: int = 1,
        camera: Optional[bpy.types.Object] = None,
        resolution: Optional[tuple] = None
    ) -> List[str]:
        """
        渲染多帧图片（用于视频）
        
        Args:
            output_folder: 输出文件夹路径
            num_frames: 帧数
            camera: 相机对象
            resolution: 分辨率
            
        Returns:
            渲染的图片路径列表
        """
        if camera is None:
            cameras = self.get_cameras()
            if cameras:
                camera = cameras[0]
            else:
                raise ValueError("未找到相机")
        
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置场景帧范围
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = num_frames
        
        rendered_files = []
        
        for frame in range(1, num_frames + 1):
            bpy.context.scene.frame_set(frame)
            
            # 渲染当前帧
            frame_output = output_dir / f"frame_{frame:04d}.png"
            self.render_image(
                output_path=str(frame_output),
                camera=camera,
                resolution=resolution
            )
            rendered_files.append(str(frame_output))
        
        return rendered_files
    
    def create_video_from_frames(
        self,
        frames_folder: str,
        output_video: str,
        fps: int = 24,
        image_pattern: str = "*.png"
    ) -> str:
        """
        从图片序列创建视频
        
        Args:
            frames_folder: 包含图片的文件夹
            output_video: 输出视频路径
            fps: 帧率
            image_pattern: 图片文件名模式，如 "*.png" 或 "frame_*.png"
            
        Returns:
            输出视频路径
        """
        frames_dir = Path(frames_folder)
        if not frames_dir.exists():
            raise ValueError(f"图片文件夹不存在: {frames_folder}")
        
        # 检查 ffmpeg 是否可用
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("ffmpeg 未安装，无法创建视频。请安装: sudo apt install ffmpeg")
        
        # 构建 ffmpeg 命令
        output_path = Path(output_video)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用 glob 模式匹配图片
        cmd = [
            "ffmpeg", "-y",
            "-r", str(fps),
            "-pattern_type", "glob",
            "-i", str(frames_dir / image_pattern),
            "-pix_fmt", "yuv420p",
            "-vcodec", "libx264",
            str(output_path)
        ]
        
        print(f"正在创建视频: {output_video}")
        print(f"命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ 视频已创建: {output_video}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"✗ 创建视频失败: {e}")
            print(f"错误输出: {e.stderr}")
            raise
    
    def render_and_create_video(
        self,
        output_folder: str,
        num_frames: int = 60,
        fps: int = 24,
        camera: Optional[bpy.types.Object] = None,
        resolution: Optional[tuple] = None
    ) -> str:
        """
        渲染多帧并创建视频（一步完成）
        
        Args:
            output_folder: 输出文件夹
            num_frames: 帧数
            fps: 帧率
            camera: 相机对象
            resolution: 分辨率
            
        Returns:
            输出视频路径
        """
        frames_dir = Path(output_folder) / "frames"
        video_path = Path(output_folder) / "output.mp4"
        
        # 渲染多帧
        print(f"正在渲染 {num_frames} 帧...")
        self.render_multiple_frames(
            output_folder=str(frames_dir),
            num_frames=num_frames,
            camera=camera,
            resolution=resolution
        )
        
        # 创建视频
        print(f"正在创建视频...")
        self.create_video_from_frames(
            frames_folder=str(frames_dir),
            output_video=str(video_path),
            fps=fps
        )
        
        return str(video_path)
    
    def render_multiple_cameras(
        self,
        output_folder: str,
        cameras: Optional[List[bpy.types.Object]] = None,
        resolution: Optional[tuple] = None,
        passes_to_save: Optional[List[str]] = None
    ) -> List[str]:
        """
        使用多个相机渲染图片
        
        Args:
            output_folder: 输出文件夹路径
            cameras: 相机对象列表（如果为None，使用场景中的所有相机）
            resolution: 分辨率 (width, height)
            passes_to_save: 要保存的通道列表
            
        Returns:
            渲染的图片路径列表
        """
        if cameras is None:
            cameras = self.get_cameras()
        
        if not cameras:
            raise ValueError("未找到相机")
        
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        rendered_files = []
        
        print(f"找到 {len(cameras)} 个相机，开始渲染...")
        
        for i, camera in enumerate(cameras):
            camera_name = camera.name.replace(" ", "_").replace(".", "_")
            output_path = output_dir / f"camera_{i+1}_{camera_name}.png"
            
            print(f"\n[{i+1}/{len(cameras)}] 渲染相机: {camera.name}")
            try:
                self.render_image(
                    output_path=str(output_path),
                    camera=camera,
                    resolution=resolution,
                    passes_to_save=passes_to_save
                )
                rendered_files.append(str(output_path))
            except Exception as e:
                print(f"  ✗ 渲染失败: {e}")
                continue
        
        print(f"\n✓ 完成！共渲染 {len(rendered_files)} 张图片")
        return rendered_files


if __name__ == "__main__":
    print("场景渲染模块")
    print("使用示例:")
    print("  renderer = SceneRenderer('scene.blend')")
    print("  renderer.render_image('output.png')")
    print("  renderer.render_and_create_video('output_folder', num_frames=60)")

