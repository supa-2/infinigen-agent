#!/usr/bin/env python
"""查找渲染图片"""
from pathlib import Path

test_dir = Path("/home/ubuntu/infinigen/outputs/test_langchain_1765279816")

print("=" * 70)
print("查找渲染图片")
print("=" * 70)

# 1. 检查预期位置
rendered_image = test_dir / "rendered_image.png"
print(f"\n1. Agent 返回的路径:")
print(f"   {rendered_image}")
print(f"   存在: {rendered_image.exists()}")

# 2. 检查 frames 目录（Infinigen 原始渲染）
frames_dir = test_dir / "frames" / "Image" / "camera_0"
if frames_dir.exists():
    print(f"\n2. Infinigen 生成的原始渲染文件:")
    for f in sorted(frames_dir.iterdir()):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   {f.name} ({size_mb:.2f} MB)")
        if f.suffix == '.exr':
            print(f"      ⚠️  这是 EXR 格式，需要转换为 PNG")

# 3. 查找所有图片
print(f"\n3. 所有图片文件:")
png_files = list(test_dir.rglob("*.png"))
exr_files = list(test_dir.rglob("*.exr"))

if png_files:
    print("   PNG 文件:")
    for png in sorted(png_files):
        size_mb = png.stat().st_size / 1024 / 1024
        rel_path = png.relative_to(test_dir)
        print(f"      {rel_path} ({size_mb:.2f} MB)")
else:
    print("   ❌ 没有找到 .png 文件")

if exr_files:
    print("\n   EXR 文件（高动态范围格式）:")
    for exr in sorted(exr_files):
        size_mb = exr.stat().st_size / 1024 / 1024
        rel_path = exr.relative_to(test_dir)
        print(f"      {rel_path} ({size_mb:.2f} MB)")
        print(f"         💡 可以使用 Blender 或图像工具转换为 PNG")

print()
print("=" * 70)
print("建议:")
if exr_files:
    print(f"  渲染图片是 EXR 格式: {exr_files[0].relative_to(test_dir)}")
    print("  可以使用以下命令查看或转换:")
    print(f"    # 在 Blender 中打开场景查看")
    print(f"    python -m infinigen.launch_blender {test_dir}/scene.blend")
    print()
    print("    # 或者使用图像工具转换 EXR 到 PNG")
    print(f"    # 需要安装: pip install imageio imageio-ffmpeg")
else:
    print("  未找到渲染图片，可能渲染步骤未完成或失败")
