#!/usr/bin/env python
"""
快速渲染测试 - 使用 Infinigen 的标准流程
"""
import subprocess
import sys
from pathlib import Path


def main():
    infinigen_root = Path("/home/ubuntu/infinigen")
    scene_path = infinigen_root / "outputs/hello_room/coarse/scene.blend"
    output_folder = infinigen_root / "outputs/hello_room/coarse/frames_render"
    
    print("="*60)
    print("快速渲染测试")
    print("="*60)
    print(f"场景: {scene_path}")
    print(f"输出: {output_folder}")
    
    if not scene_path.exists():
        print(f"✗ 场景文件不存在")
        return
    
    print(f"✓ 场景文件存在")
    
    # 使用 Infinigen 的标准渲染命令
    cmd = [
        sys.executable,
        "-m", "infinigen_examples.generate_indoors",
        "--seed", "0",
        "--task", "render",
        "--input_folder", str(scene_path.parent),
        "--output_folder", str(output_folder)
    ]
    
    print(f"\n执行命令:")
    print(" ".join(cmd))
    print("\n正在渲染（这可能需要几分钟）...")
    print("提示: 渲染过程会显示进度信息")
    
    try:
        # 运行渲染命令，实时显示输出
        process = subprocess.Popen(
            cmd,
            cwd=str(infinigen_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 实时打印输出
        for line in process.stdout:
            print(line, end='')
            # 如果看到关键信息，可以提前结束
            if "error" in line.lower() or "failed" in line.lower():
                break
        
        process.wait()
        
        if process.returncode == 0:
            print("\n✓ 渲染命令执行完成")
            
            # 检查输出
            if output_folder.exists():
                image_files = list(output_folder.rglob("*.png"))
                if image_files:
                    print(f"\n✓ 找到 {len(image_files)} 个图片文件:")
                    for img in image_files[:5]:
                        size_mb = img.stat().st_size / 1024 / 1024
                        print(f"  - {img.relative_to(infinigen_root)} ({size_mb:.2f} MB)")
                    return True
                else:
                    print("\n⚠ 未找到图片文件")
                    print(f"输出文件夹内容: {list(output_folder.iterdir())}")
            else:
                print(f"\n⚠ 输出文件夹不存在: {output_folder}")
        else:
            print(f"\n✗ 渲染失败 (退出码: {process.returncode})")
            
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

