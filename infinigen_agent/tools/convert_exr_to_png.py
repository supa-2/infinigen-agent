#!/usr/bin/env python
"""将 EXR 文件转换为 PNG - 简单易用的转换工具"""
import sys
import argparse
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("❌ 缺少 numpy 库")
    print("请安装: pip install numpy")
    sys.exit(1)

# 尝试多种方式读取 EXR
try:
    import OpenEXR
    import Imath
    HAS_OPENEXR = True
except ImportError:
    HAS_OPENEXR = False

try:
    import imageio
    import imageio.v2 as imageio_v2
    HAS_IMAGEIO = True
except ImportError:
    HAS_IMAGEIO = False

if not HAS_OPENEXR and not HAS_IMAGEIO:
    print("❌ 缺少 EXR 读取库")
    print("请安装以下之一：")
    print("  - pip install OpenEXR (推荐)")
    print("  - pip install imageio imageio-ffmpeg")
    sys.exit(1)

def convert_exr_to_png(exr_path, png_path=None, verbose=True):
    """
    将 EXR 文件转换为 PNG
    
    Args:
        exr_path: EXR 文件路径
        png_path: PNG 输出路径（如果为 None，自动生成）
        verbose: 是否显示详细信息
    
    Returns:
        成功返回 PNG 路径，失败返回 None
    """
    exr_path = Path(exr_path)
    
    if not exr_path.exists():
        if verbose:
            print(f"❌ EXR 文件不存在: {exr_path}")
        return None
    
    # 如果没有指定输出路径，自动生成
    if png_path is None:
        png_path = exr_path.with_suffix('.png')
    else:
        png_path = Path(png_path)
    
    try:
        # 读取 EXR 文件
        if verbose:
            print(f"📖 读取 EXR 文件: {exr_path}")
        
        # 方法1: 使用 OpenEXR 库（推荐，更可靠）
        if HAS_OPENEXR:
            try:
                exr_file = OpenEXR.InputFile(str(exr_path))
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
                        # 如果没有 RGB，尝试使用第一个可用通道
                        available_channels = list(exr_file.header()['channels'].keys())
                        if available_channels:
                            channel_data[channel] = exr_file.channel(available_channels[0], Imath.PixelType(Imath.PixelType.FLOAT))
                
                # 转换为 numpy 数组
                if len(channel_data) >= 3:
                    r = np.frombuffer(channel_data['R'], dtype=np.float32).reshape((height, width))
                    g = np.frombuffer(channel_data['G'], dtype=np.float32).reshape((height, width))
                    b = np.frombuffer(channel_data['B'], dtype=np.float32).reshape((height, width))
                    exr_image = np.stack([r, g, b], axis=2)
                elif len(channel_data) == 1:
                    # 单通道，转换为 RGB
                    channel_name = list(channel_data.keys())[0]
                    single = np.frombuffer(channel_data[channel_name], dtype=np.float32).reshape((height, width))
                    exr_image = np.stack([single, single, single], axis=2)
                else:
                    raise ValueError(f"无法读取 EXR 通道，找到 {len(channel_data)} 个通道")
                
                exr_file.close()
                if verbose:
                    print(f"   使用 OpenEXR 库读取")
            except Exception as e:
                if verbose:
                    print(f"   OpenEXR 读取失败: {e}，尝试 imageio...")
                # 如果 OpenEXR 失败，尝试 imageio
                if HAS_IMAGEIO:
                    exr_image = imageio_v2.imread(str(exr_path))
                    if verbose:
                        print(f"   使用 imageio 读取")
                else:
                    raise
        # 方法2: 使用 imageio
        elif HAS_IMAGEIO:
            exr_image = imageio_v2.imread(str(exr_path))
            if verbose:
                print(f"   使用 imageio 读取")
        else:
            raise RuntimeError("没有可用的 EXR 读取库")
        
        if verbose:
            print(f"   形状: {exr_image.shape}")
            print(f"   数据类型: {exr_image.dtype}")
            print(f"   值范围: {exr_image.min():.4f} - {exr_image.max():.4f}")
        
        # 转换为 uint8，应用 tone mapping 和 gamma 校正
        if exr_image.dtype != np.uint8:
            max_val = exr_image.max()
            min_val = exr_image.min()
            
            if verbose:
                print(f"   原始值范围: {min_val:.4f} - {max_val:.4f}")
            
            # 处理负值（可能是浮点误差）
            if min_val < 0:
                if verbose:
                    print(f"   修正负值（可能是浮点误差）")
                exr_image = np.maximum(exr_image, 0)
            
            # 应用 exposure 调整（可选，默认 1.0）
            exposure = 1.0  # 可以根据需要调整
            if exposure != 1.0:
                exr_image = exr_image * exposure
                if verbose:
                    print(f"   应用 exposure: {exposure}")
            
            # Tone mapping（处理 HDR）
            if max_val > 1.0:
                if verbose:
                    print(f"   使用 tone mapping (HDR 值 > 1.0)")
                # 改进的 Reinhard tone mapping
                # 使用更温和的映射，保留更多细节
                exr_image = exr_image / (1 + exr_image * 0.8)  # 调整系数以保留更多细节
            else:
                # 值在 0-1 范围内，但可能仍然需要调整
                if verbose:
                    print(f"   值在 0-1 范围内，直接处理")
            
            # 确保值在 0-1 范围内
            exr_image = np.clip(exr_image, 0, 1)
            
            # 应用 gamma 校正（线性空间 → sRGB）
            # EXR 是线性空间，但 PNG 需要 sRGB 空间
            gamma = 2.2  # 标准 gamma 值
            if verbose:
                print(f"   应用 gamma 校正: {gamma}")
            exr_image = np.power(exr_image, 1.0 / gamma)
            
            # 转换为 uint8
            exr_image = (exr_image * 255).astype(np.uint8)
        
        # 如果是多通道，只取前3个通道（RGB）
        if len(exr_image.shape) == 3 and exr_image.shape[2] > 3:
            if verbose:
                print(f"   提取 RGB 通道（原 {exr_image.shape[2]} 通道）")
            exr_image = exr_image[:, :, :3]
        
        # 如果是灰度图，转换为 RGB
        if len(exr_image.shape) == 2:
            if verbose:
                print(f"   灰度图转换为 RGB")
            exr_image = np.stack([exr_image, exr_image, exr_image], axis=2)
        
        # 确保输出目录存在
        png_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存为 PNG
        if verbose:
            print(f"💾 保存 PNG 文件: {png_path}")
        
        # 使用 imageio 保存 PNG
        if HAS_IMAGEIO:
            imageio_v2.imwrite(str(png_path), exr_image)
        else:
            # 如果没有 imageio，使用 PIL
            from PIL import Image
            Image.fromarray(exr_image).save(str(png_path))
        
        if verbose:
            file_size = png_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ 转换成功！")
            print(f"   输出文件: {png_path}")
            print(f"   文件大小: {file_size:.2f} MB")
        
        return str(png_path)
    except Exception as e:
        if verbose:
            print(f"❌ 转换失败: {e}")
            import traceback
            traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将 EXR 文件转换为 PNG")
    parser.add_argument("exr_path", help="EXR 文件路径")
    parser.add_argument("-o", "--output", help="PNG 输出路径（默认：同目录同名.png）")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式（不显示详细信息）")
    
    args = parser.parse_args()
    
    result = convert_exr_to_png(args.exr_path, args.output, verbose=not args.quiet)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
