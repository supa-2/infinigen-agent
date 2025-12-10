#!/usr/bin/env python
"""测试 EXR 转 PNG 转换功能"""
import sys
from pathlib import Path

# 添加项目路径
infinigen_root = Path(__file__).parent.parent
sys.path.insert(0, str(infinigen_root))

def test_exr_conversion():
    """测试 EXR 转 PNG 转换"""
    print("=" * 70)
    print("测试 EXR 转 PNG 转换功能")
    print("=" * 70)
    
    # 检查 imageio 是否安装
    try:
        import imageio
        import numpy as np
        print("✅ imageio 和 numpy 已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("请安装: pip install imageio imageio-ffmpeg")
        return False
    
    # 查找 EXR 文件
    test_dir = Path("outputs/test_langchain_1765279816")
    exr_path = test_dir / "frames" / "Image" / "camera_0" / "Image_0_0_0001_0.exr"
    png_path = test_dir / "rendered_image.png"
    
    print(f"\n查找 EXR 文件:")
    print(f"  路径: {exr_path}")
    
    if not exr_path.exists():
        print(f"❌ EXR 文件不存在: {exr_path}")
        # 尝试查找其他 EXR 文件
        frames_dir = test_dir / "frames" / "Image" / "camera_0"
        if frames_dir.exists():
            exr_files = list(frames_dir.glob("*.exr"))
            if exr_files:
                print(f"  找到其他 EXR 文件:")
                for f in exr_files:
                    print(f"    {f.name}")
                exr_path = exr_files[0]
            else:
                print(f"  frames 目录中没有 EXR 文件")
                return False
        else:
            print(f"  frames 目录不存在")
            return False
    
    print(f"✅ 找到 EXR 文件: {exr_path}")
    print(f"  文件大小: {exr_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # 读取 EXR 文件
    print(f"\n读取 EXR 文件...")
    try:
        exr_image = imageio.imread(str(exr_path))
        print(f"✅ EXR 文件读取成功")
        print(f"  图像形状: {exr_image.shape}")
        print(f"  数据类型: {exr_image.dtype}")
        print(f"  值范围: {exr_image.min():.4f} - {exr_image.max():.4f}")
        print(f"  平均值: {exr_image.mean():.4f}")
    except Exception as e:
        print(f"❌ 读取 EXR 文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 转换为 uint8
    print(f"\n转换为 uint8...")
    try:
        if exr_image.dtype != np.uint8:
            print(f"  原始类型: {exr_image.dtype}")
            print(f"  原始最大值: {exr_image.max():.4f}")
            
            if exr_image.max() <= 1.0:
                print(f"  使用简单缩放 (0-1 -> 0-255)")
                png_image = (exr_image * 255).astype(np.uint8)
            else:
                print(f"  使用 tone mapping (Reinhard)")
                # Reinhard tone mapping: L_out = L_in / (1 + L_in)
                png_image = exr_image / (1 + exr_image)
                png_image = (np.clip(png_image, 0, 1) * 255).astype(np.uint8)
            
            print(f"  转换后类型: {png_image.dtype}")
            print(f"  转换后值范围: {png_image.min()} - {png_image.max()}")
        else:
            png_image = exr_image
            print(f"  已经是 uint8 格式")
    except Exception as e:
        print(f"❌ 类型转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 处理通道数
    print(f"\n处理图像通道...")
    if len(png_image.shape) == 3 and png_image.shape[2] > 3:
        print(f"  原始通道数: {png_image.shape[2]}")
        print(f"  只保留前 3 个通道 (RGB)")
        png_image = png_image[:, :, :3]
        print(f"  处理后形状: {png_image.shape}")
    elif len(png_image.shape) == 2:
        print(f"  灰度图像，转换为 RGB")
        png_image = np.stack([png_image] * 3, axis=2)
        print(f"  处理后形状: {png_image.shape}")
    
    # 保存为 PNG
    print(f"\n保存 PNG 文件...")
    print(f"  输出路径: {png_path}")
    try:
        # 确保输出目录存在
        png_path.parent.mkdir(parents=True, exist_ok=True)
        
        imageio.imwrite(str(png_path), png_image)
        
        if png_path.exists():
            print(f"✅ PNG 文件保存成功")
            print(f"  文件大小: {png_path.stat().st_size / 1024 / 1024:.2f} MB")
            print(f"  完整路径: {png_path.absolute()}")
            return True
        else:
            print(f"❌ PNG 文件保存失败（文件不存在）")
            return False
    except Exception as e:
        print(f"❌ 保存 PNG 文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_exr_conversion()
    sys.exit(0 if success else 1)
