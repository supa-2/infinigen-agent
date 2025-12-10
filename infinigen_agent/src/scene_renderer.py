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
    
    def render_preview(
        self,
        output_path: str,
        camera: Optional[bpy.types.Object] = None,
        resolution: tuple = (1920, 1080),
        engine: str = "BLENDER_EEVEE"
    ) -> str:
        """
        快速预览渲染（使用 Workbench 或 Eevee 引擎，<1秒）
        
        Args:
            output_path: 输出图片路径
            camera: 相机对象（如果为None，使用场景默认相机）
            resolution: 分辨率 (width, height)
            engine: 渲染引擎，"BLENDER_EEVEE" 或 "BLENDER_WORKBENCH"
            
        Returns:
            输出文件路径
        """
        if camera is None:
            cameras = self.get_cameras()
            if cameras:
                camera = cameras[0]
                print(f"✓ 使用相机: {camera.name}")
            else:
                raise ValueError("未找到相机")
        
        # 设置活动相机
        bpy.context.scene.camera = camera
        
        # 设置渲染引擎
        if engine not in ["BLENDER_EEVEE", "BLENDER_WORKBENCH"]:
            raise ValueError(f"不支持的渲染引擎: {engine}，请使用 BLENDER_EEVEE 或 BLENDER_WORKBENCH")
        
        bpy.context.scene.render.engine = engine
        
        # 设置分辨率
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]
        
        # 设置输出格式
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.image_settings.color_mode = "RGB"
        bpy.context.scene.render.image_settings.color_depth = "8"
        
        # 如果是 Eevee，设置快速采样
        if engine == "BLENDER_EEVEE":
            bpy.context.scene.eevee.taa_render_samples = 16  # 低采样，快速渲染
        
        # 如果是 Workbench，设置快速模式
        elif engine == "BLENDER_WORKBENCH":
            bpy.context.scene.display.shading.light = "FLAT"  # 平面着色，最快
            bpy.context.scene.display.shading.color_type = "MATERIAL"  # 材质颜色
        
        # 设置输出路径
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        bpy.context.scene.render.filepath = str(output_path)
        
        # 渲染
        print(f"⚡ 使用 {engine} 快速预览渲染中...")
        import time
        start_time = time.time()
        bpy.ops.render.render(write_still=True)
        render_time = time.time() - start_time
        print(f"✓ 快速预览渲染完成（耗时: {render_time:.2f} 秒）")
        
        return output_path
    
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
        passes_to_save: Optional[List[str]] = None,
        save_all_passes: bool = False  # 默认只保存最终图像（更快，文件更少）
    ) -> str:
        """
        渲染单张图片
        
        Args:
            output_path: 输出图片路径
            camera: 相机对象（如果为None，使用场景默认相机）
            resolution: 分辨率 (width, height)，如果为None使用场景设置
            passes_to_save: 要保存的通道列表，如 ["Image", "Depth"]
            save_all_passes: 如果为True，保存所有渲染通道（像官方命令一样）
                           默认 False，只保存最终图像（更快，文件更少）
                           如果为True，直接输出 PNG，不需要 EXR 转换
            
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
        if save_all_passes:
            # 保存所有通道（像官方命令一样）
            passes_to_save = [
                ("diffuse_direct", "DiffDir"),
                ("diffuse_color", "DiffCol"),
                ("diffuse_indirect", "DiffInd"),
                ("glossy_direct", "GlossDir"),
                ("glossy_color", "GlossCol"),
                ("glossy_indirect", "GlossInd"),
                ("transmission_direct", "TransDir"),
                ("transmission_color", "TransCol"),
                ("transmission_indirect", "TransInd"),
                ("volume_direct", "VolumeDir"),
                ("emit", "Emit"),
                ("environment", "Env"),
                ("ambient_occlusion", "AO"),
                ("Image", "Image"),  # 最终合成图像
            ]
            print(f"✓ 将保存所有渲染通道（共 {len(passes_to_save)} 个）")
        elif passes_to_save is None:
            # 默认只保存最终图像（更快，文件更少）
            passes_to_save = [("Image", "Image")]
            print(f"✓ 只保存最终图像（Image 通道）")
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
            
            # 查找渲染的图片文件并复制/转换为输出路径
            # Infinigen默认生成EXR格式，需要查找EXR文件并转换为PNG
            import shutil
            
            # 如果保存了所有通道，frames_folder 中会有多个子目录
            # Infinigen 会同时输出 PNG 和 EXR，我们优先使用 PNG（不需要转换）
            if save_all_passes:
                # 所有通道已经保存在 frames_folder 的子目录中
                # Infinigen 默认会输出 PNG（因为 saving_ground_truth=False）
                # 只需要找到 Image 通道作为主要输出
                image_dir = frames_folder / "Image" / "camera_0"
                if image_dir.exists():
                    # 优先查找 PNG（官方命令会直接输出 PNG，不需要转换）
                    rendered_files = list(image_dir.glob("Image_*.png"))
                    if not rendered_files:
                        # 如果没找到 PNG，再找 EXR（可能需要转换）
                        rendered_files = list(image_dir.glob("Image_*.exr"))
                else:
                    # 尝试其他可能的路径
                    image_dirs = list(frames_folder.glob("Image*"))
                    for img_dir in image_dirs:
                        if img_dir.is_dir():
                            # 优先 PNG
                            rendered_files = list(img_dir.glob("**/Image_*.png"))
                            if not rendered_files:
                                rendered_files = list(img_dir.glob("**/Image_*.exr"))
                            if rendered_files:
                                break
                    if not rendered_files:
                        rendered_files = []
            else:
                # 方法1: 直接在frames文件夹中查找（先找PNG，再找EXR）
                rendered_files = list(frames_folder.glob("Image_*.png"))
                
                # 方法2: 在camera子目录中查找（reorganize后）
                if not rendered_files:
                    camera_dirs = list(frames_folder.glob("camera_*"))
                    for cam_dir in camera_dirs:
                        if cam_dir.is_dir():
                            rendered_files.extend(list(cam_dir.glob("Image_*.png")))
                
                # 方法3: 如果没找到PNG，查找EXR文件（Infinigen默认格式）
                if not rendered_files:
                    rendered_files = list(frames_folder.glob("Image_*.exr"))
                    if not rendered_files:
                        camera_dirs = list(frames_folder.glob("camera_*"))
                        for cam_dir in camera_dirs:
                            if cam_dir.is_dir():
                                rendered_files.extend(list(cam_dir.glob("Image_*.exr")))
            
            if rendered_files:
                source_file = rendered_files[0]
                
                # 默认 save_all_passes=True，Infinigen 会直接输出 PNG
                # 只有在找不到 PNG 时才需要转换 EXR（这种情况很少见）
                if source_file.suffix.lower() == '.exr':
                    print(f"⚠ 注意：找到了 EXR 文件，但通常应该有 PNG 文件（save_all_passes=True）")
                    print(f"   将转换 EXR 为 PNG...")
                    try:
                        import numpy as np
                        
                        # 尝试使用 OpenEXR 库（更可靠）
                        try:
                            import OpenEXR
                            import Imath
                            use_openexr = True
                        except ImportError:
                            use_openexr = False
                            try:
                                import imageio
                                import imageio.v2 as imageio_v2
                            except ImportError:
                                raise ImportError("需要安装 OpenEXR 或 imageio: pip install OpenEXR")
                        
                        # 读取 EXR 文件
                        print(f"📖 读取 EXR 文件: {source_file}")
                        
                        if use_openexr:
                            # 使用 OpenEXR 库读取
                            exr_file = OpenEXR.InputFile(str(source_file))
                            header = exr_file.header()
                            dw = header['dataWindow']
                            width = dw.max.x - dw.min.x + 1
                            height = dw.max.y - dw.min.y + 1
                            
                            # 读取 RGB 通道
                            channels = ['R', 'G', 'B']
                            channel_data = {}
                            for channel in channels:
                                if channel in exr_file.header()['channels']:
                                    channel_data[channel] = exr_file.channel(channel, Imath.PixelType(Imath.PixelType.FLOAT))
                                else:
                                    available_channels = list(exr_file.header()['channels'].keys())
                                    if available_channels:
                                        channel_data[channel] = exr_file.channel(available_channels[0], Imath.PixelType(Imath.PixelType.FLOAT))
                            
                            if len(channel_data) >= 3:
                                r = np.frombuffer(channel_data['R'], dtype=np.float32).reshape((height, width))
                                g = np.frombuffer(channel_data['G'], dtype=np.float32).reshape((height, width))
                                b = np.frombuffer(channel_data['B'], dtype=np.float32).reshape((height, width))
                                exr_image = np.stack([r, g, b], axis=2)
                            elif len(channel_data) == 1:
                                channel_name = list(channel_data.keys())[0]
                                single = np.frombuffer(channel_data[channel_name], dtype=np.float32).reshape((height, width))
                                exr_image = np.stack([single, single, single], axis=2)
                            else:
                                raise ValueError(f"无法读取 EXR 通道")
                            exr_file.close()
                        else:
                            # 使用 imageio 读取
                            exr_image = imageio_v2.imread(str(source_file))
                        
                        # EXR 通常是浮点数，需要转换为 0-255 范围的 uint8
                        # 应用 tone mapping 和 gamma 校正以改善光照
                        if exr_image.dtype != np.uint8:
                            max_val = exr_image.max()
                            min_val = exr_image.min()
                            
                            # 处理负值（可能是浮点误差）
                            if min_val < 0:
                                exr_image = np.maximum(exr_image, 0)
                            
                            # Tone mapping（处理 HDR）
                            if max_val > 1.0:
                                print(f"   使用 tone mapping (值范围: {min_val:.2f} - {max_val:.2f})")
                                # 改进的 Reinhard tone mapping，保留更多细节
                                exr_image = exr_image / (1 + exr_image * 0.8)
                            else:
                                print(f"   值在 0-1 范围内")
                            
                            # 确保值在 0-1 范围内
                            exr_image = np.clip(exr_image, 0, 1)
                            
                            # 应用 gamma 校正（线性空间 → sRGB）
                            # EXR 是线性空间，但 PNG 需要 sRGB 空间
                            print(f"   应用 gamma 校正 (2.2)")
                            exr_image = np.power(exr_image, 1.0 / 2.2)
                            
                            # 转换为 uint8
                            exr_image = (exr_image * 255).astype(np.uint8)
                        
                        # 如果是多通道，只取前3个通道（RGB）
                        if len(exr_image.shape) == 3 and exr_image.shape[2] > 3:
                            exr_image = exr_image[:, :, :3]
                        
                        # 如果是灰度图，转换为 RGB
                        if len(exr_image.shape) == 2:
                            exr_image = np.stack([exr_image, exr_image, exr_image], axis=2)
                        
                        # 保存为 PNG
                        try:
                            import imageio
                            import imageio.v2 as imageio_v2
                            imageio_v2.imwrite(str(output_path), exr_image)
                        except ImportError:
                            # 如果没有 imageio，使用 PIL
                            from PIL import Image
                            Image.fromarray(exr_image).save(str(output_path))
                        print(f"✓ EXR 已转换为 PNG: {output_path}")
                    except ImportError as e:
                        print(f"⚠ 无法转换 EXR 到 PNG: 缺少必要的库")
                        print(f"  请安装: pip install OpenEXR imageio")
                        print(f"  错误: {e}")
                        print(f"  原始 EXR 文件: {source_file}")
                        # 如果转换失败，至少复制 EXR 文件
                        shutil.copy2(source_file, output_path.with_suffix('.exr'))
                        return str(output_path.with_suffix('.exr'))
                    except Exception as e:
                        print(f"⚠ EXR 转换失败: {e}")
                        import traceback
                        traceback.print_exc()
                        print(f"  原始 EXR 文件: {source_file}")
                        # 如果转换失败，至少复制 EXR 文件
                        exr_output = output_path.with_suffix('.exr')
                        shutil.copy2(source_file, exr_output)
                        print(f"  已复制 EXR 文件到: {exr_output}")
                        return str(exr_output)
                else:
                    # 如果是 PNG，直接复制（save_all_passes=True 时直接输出 PNG，不需要转换）
                    if save_all_passes:
                        print(f"✓ PNG 图片已复制到: {output_path}（无需转换）")
                    else:
                        print(f"✓ PNG 图片已复制到: {output_path}")
                    shutil.copy2(source_file, output_path)
                
                # 如果保存了所有通道，保留 frames 目录；否则清理临时目录
                if not save_all_passes:
                    try:
                        shutil.rmtree(frames_folder)
                    except Exception:
                        pass  # 忽略清理错误
                else:
                    # 将所有通道复制到输出目录的父目录
                    output_dir = Path(output_path).parent
                    frames_output_dir = output_dir / "frames"
                    if frames_output_dir.exists():
                        import shutil
                        shutil.rmtree(frames_output_dir)
                    shutil.copytree(frames_folder, frames_output_dir)
                    print(f"✓ 所有渲染通道已保存到: {frames_output_dir}")
            else:
                print(f"⚠ 未在临时 frames 目录找到渲染文件")
                print(f"  检查目录: {frames_folder}")
                # 尝试从原始场景的 frames 目录查找（场景生成时已经渲染过）
                scene_frames_dir = Path(self.scene_path).parent / "frames" / "Image" / "camera_0"
                if scene_frames_dir.exists():
                    exr_files = list(scene_frames_dir.glob("Image_*.exr"))
                    if exr_files:
                        print(f"  找到原始 EXR 文件: {exr_files[0]}")
                        # 尝试转换 EXR 到 PNG
                        try:
                            import numpy as np
                            
                            # 尝试使用 OpenEXR
                            try:
                                import OpenEXR
                                import Imath
                                use_openexr = True
                            except ImportError:
                                use_openexr = False
                                try:
                                    import imageio
                                    import imageio.v2 as imageio_v2
                                except ImportError:
                                    raise ImportError("需要安装 OpenEXR 或 imageio")
                            
                            print(f"📖 读取原始 EXR 文件: {exr_files[0]}")
                            
                            if use_openexr:
                                exr_file = OpenEXR.InputFile(str(exr_files[0]))
                                header = exr_file.header()
                                dw = header['dataWindow']
                                width = dw.max.x - dw.min.x + 1
                                height = dw.max.y - dw.min.y + 1
                                
                                channels = ['R', 'G', 'B']
                                channel_data = {}
                                for channel in channels:
                                    if channel in exr_file.header()['channels']:
                                        channel_data[channel] = exr_file.channel(channel, Imath.PixelType(Imath.PixelType.FLOAT))
                                    else:
                                        available_channels = list(exr_file.header()['channels'].keys())
                                        if available_channels:
                                            channel_data[channel] = exr_file.channel(available_channels[0], Imath.PixelType(Imath.PixelType.FLOAT))
                                
                                if len(channel_data) >= 3:
                                    r = np.frombuffer(channel_data['R'], dtype=np.float32).reshape((height, width))
                                    g = np.frombuffer(channel_data['G'], dtype=np.float32).reshape((height, width))
                                    b = np.frombuffer(channel_data['B'], dtype=np.float32).reshape((height, width))
                                    exr_image = np.stack([r, g, b], axis=2)
                                elif len(channel_data) == 1:
                                    channel_name = list(channel_data.keys())[0]
                                    single = np.frombuffer(channel_data[channel_name], dtype=np.float32).reshape((height, width))
                                    exr_image = np.stack([single, single, single], axis=2)
                                exr_file.close()
                            else:
                                exr_image = imageio_v2.imread(str(exr_files[0]))
                            if exr_image.dtype != np.uint8:
                                max_val = exr_image.max()
                                min_val = exr_image.min()
                                
                                # 处理负值
                                if min_val < 0:
                                    exr_image = np.maximum(exr_image, 0)
                                
                                # Tone mapping
                                if max_val > 1.0:
                                    print(f"   使用 tone mapping (值范围: {min_val:.2f} - {max_val:.2f})")
                                    exr_image = exr_image / (1 + exr_image * 0.8)
                                
                                # 确保值在 0-1 范围内
                                exr_image = np.clip(exr_image, 0, 1)
                                
                                # 应用 gamma 校正
                                print(f"   应用 gamma 校正 (2.2)")
                                exr_image = np.power(exr_image, 1.0 / 2.2)
                                
                                # 转换为 uint8
                                exr_image = (exr_image * 255).astype(np.uint8)
                            if len(exr_image.shape) == 3 and exr_image.shape[2] > 3:
                                exr_image = exr_image[:, :, :3]
                            if len(exr_image.shape) == 2:
                                exr_image = np.stack([exr_image, exr_image, exr_image], axis=2)
                            
                            try:
                                import imageio
                                import imageio.v2 as imageio_v2
                                imageio_v2.imwrite(str(output_path), exr_image)
                            except ImportError:
                                from PIL import Image
                                Image.fromarray(exr_image).save(str(output_path))
                            print(f"✓ 从原始 frames 目录转换 EXR 到 PNG: {output_path}")
                            return output_path
                        except ImportError as e:
                            print(f"⚠ 无法转换 EXR: 缺少必要的库")
                            print(f"  请安装: pip install OpenEXR imageio")
                            print(f"  错误: {e}")
                            print(f"  原始 EXR 文件: {exr_files[0]}")
                            # 如果转换失败，至少复制 EXR 文件
                            exr_output = output_path.with_suffix('.exr')
                            shutil.copy2(exr_files[0], exr_output)
                            print(f"  已复制 EXR 文件到: {exr_output}")
                            return str(exr_output)
                        except Exception as e:
                            print(f"⚠ EXR 转换失败: {e}")
                            import traceback
                            traceback.print_exc()
                            # 如果转换失败，至少复制 EXR 文件
                            exr_output = output_path.with_suffix('.exr')
                            shutil.copy2(exr_files[0], exr_output)
                            print(f"  已复制 EXR 文件到: {exr_output}")
                            return str(exr_output)
                    else:
                        print(f"  原始 frames 目录中也没有找到 EXR 文件")
                else:
                    print(f"  原始 frames 目录不存在: {scene_frames_dir}")
            
            # 如果找到了文件（无论是PNG还是EXR），返回路径
            if rendered_files:
                print(f"✓ 图片已渲染到: {output_path}")
                return output_path
            else:
                print(f"⚠ 未找到渲染文件")
                return None
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

