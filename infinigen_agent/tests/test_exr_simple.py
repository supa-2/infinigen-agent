#!/usr/bin/env python3
"""简单测试 EXR 转 PNG"""
from pathlib import Path
import sys

try:
    import imageio
    import numpy as np
    print("✅ 依赖库已安装")
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    sys.exit(1)

exr_path = Path("outputs/test_langchain_1765279816/frames/Image/camera_0/Image_0_0_0001_0.exr")
png_path = Path("outputs/test_langchain_1765279816/rendered_image.png")

print(f"EXR 文件: {exr_path}")
print(f"存在: {exr_path.exists()}")

if not exr_path.exists():
    print("❌ EXR 文件不存在")
    sys.exit(1)

print(f"✅ 找到 EXR 文件 ({exr_path.stat().st_size / 1024 / 1024:.2f} MB)")

print("\n读取 EXR...")
exr_image = imageio.imread(str(exr_path))
print(f"✅ 读取成功")
print(f"  形状: {exr_image.shape}")
print(f"  类型: {exr_image.dtype}")
print(f"  范围: {exr_image.min():.4f} - {exr_image.max():.4f}")

print("\n转换...")
if exr_image.dtype != np.uint8:
    if exr_image.max() <= 1.0:
        png_image = (exr_image * 255).astype(np.uint8)
    else:
        png_image = exr_image / (1 + exr_image)
        png_image = (np.clip(png_image, 0, 1) * 255).astype(np.uint8)

if len(png_image.shape) == 3 and png_image.shape[2] > 3:
    png_image = png_image[:, :, :3]

print(f"✅ 转换完成")
print(f"  形状: {png_image.shape}")
print(f"  类型: {png_image.dtype}")

print(f"\n保存 PNG...")
png_path.parent.mkdir(parents=True, exist_ok=True)
imageio.imwrite(str(png_path), png_image)

if png_path.exists():
    print(f"✅ PNG 保存成功: {png_path}")
    print(f"  大小: {png_path.stat().st_size / 1024 / 1024:.2f} MB")
else:
    print("❌ PNG 保存失败")
    sys.exit(1)
