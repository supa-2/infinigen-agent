#!/usr/bin/env python
"""
简单的渲染测试 - 使用 Infinigen 的命令行方式
"""
import subprocess
import sys
from pathlib import Path


def test_render_with_infinigen():
    """使用 Infinigen 的命令行方式渲染"""
    print("="*60)
    print("测试渲染功能（使用 Infinigen 命令行）")
    print("="*60)
    
    # 使用绝对路径
    infinigen_root = Path(__file__).parent.parent.absolute()
    scene_path = infinigen_root / "outputs/hello_room/coarse/scene.blend"
    
    if not scene_path.exists():
        print(f"✗ 场景文件不存在: {scene_path}")
        return False
    
    print(f"✓ 场景文件存在: {scene_path}")
    print(f"文件大小: {scene_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # 输出文件夹
    output_folder = infinigen_root / "outputs/hello_room/coarse/frames_test"
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"\n正在渲染图片到: {output_folder}")
    print("使用命令: python -m infinigen_examples.generate_indoors --task render")
    
    cmd = [
        sys.executable,
        "-m", "infinigen_examples.generate_indoors",
        "--seed", "0",
        "--task", "render",
        "--input_folder", str(scene_path.parent),
        "--output_folder", str(output_folder)
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(infinigen_root),
            timeout=300,  # 5分钟超时
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✓ 渲染命令执行成功")
            print(f"输出文件夹: {output_folder}")
            
            # 检查输出文件
            image_files = list(output_folder.glob("**/*.png"))
            if image_files:
                print(f"\n找到 {len(image_files)} 个图片文件:")
                for img in image_files[:5]:  # 只显示前5个
                    print(f"  - {img}")
                if len(image_files) > 5:
                    print(f"  ... 还有 {len(image_files) - 5} 个文件")
                return True
            else:
                print("⚠ 未找到图片文件")
                print(f"输出内容: {result.stdout[-500:]}")
                return False
        else:
            print(f"\n✗ 渲染命令失败 (退出码: {result.returncode})")
            print(f"错误输出: {result.stderr[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ 渲染超时（超过5分钟）")
        return False
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_render_with_infinigen()
    print("\n" + "="*60)
    print(f"测试结果: {'✓ 成功' if success else '✗ 失败'}")
    print("="*60)

