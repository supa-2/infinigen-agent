#!/usr/bin/env python3
"""
直接生成室内场景
"""
import subprocess
import sys
from pathlib import Path
import time

print("="*60)
print("开始生成室内场景")
print("="*60)
print()

infinigen_root = Path("/home/ubuntu/infinigen")
output_folder = "/tmp/test_scene_direct"

# 清理旧输出
import shutil
if Path(output_folder).exists():
    print(f"清理旧输出文件夹: {output_folder}")
    shutil.rmtree(output_folder)

# 构建命令
cmd = [
    sys.executable,
    '-m', 'infinigen_examples.generate_indoors',
    '--output_folder', output_folder,
    '-s', '0',
    '-g', 'base', 'disable/no_objects',
    '-t', 'coarse'
]

print(f"执行命令: {' '.join(cmd)}")
print(f"工作目录: {infinigen_root}")
print(f"输出文件夹: {output_folder}")
print()
print("开始生成场景（这可能需要几分钟）...")
print()

start_time = time.time()

try:
    # 运行命令，实时输出
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
        print(line, end='', flush=True)
    
    process.wait()
    
    elapsed_time = time.time() - start_time
    
    print()
    print("="*60)
    
    if process.returncode == 0:
        print(f"✓ 场景生成成功！（耗时: {elapsed_time:.1f}秒）")
        print()
        
        # 检查输出文件
        output_path = Path(output_folder)
        if output_path.exists():
            blend_files = list(output_path.rglob("*.blend"))
            if blend_files:
                print(f"✓ 找到 {len(blend_files)} 个场景文件:")
                for f in blend_files[:5]:
                    size = f.stat().st_size / (1024*1024)  # MB
                    print(f"  - {f} ({size:.2f} MB)")
            else:
                print("⚠ 未找到 .blend 文件")
                print(f"输出目录内容: {list(output_path.iterdir())}")
        else:
            print(f"⚠ 输出目录不存在: {output_folder}")
    else:
        print(f"✗ 场景生成失败（退出码: {process.returncode}）")
        print(f"耗时: {elapsed_time:.1f}秒")
        
except KeyboardInterrupt:
    print("\n\n用户中断")
    process.kill()
except Exception as e:
    print(f"\n✗ 执行失败: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
