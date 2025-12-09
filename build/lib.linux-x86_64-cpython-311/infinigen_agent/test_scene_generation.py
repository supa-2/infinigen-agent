#!/usr/bin/env python3
"""
直接测试 Infinigen 场景生成功能
"""
import subprocess
import sys
from pathlib import Path

print("="*60)
print("测试 Infinigen 场景生成功能")
print("="*60)
print()

# 检查 landlab
print("[1] 检查 landlab 模块...")
try:
    import landlab
    print(f"  ✓ landlab 已安装 (版本: {landlab.__version__ if hasattr(landlab, '__version__') else '未知'})")
except ImportError:
    print("  ✗ landlab 未安装")
    print("  需要安装: pip install .[terrain]")
    print()
    print("是否继续测试？(y/n): ", end="", flush=True)
    # 继续测试，看看具体错误

print()
print("[2] 尝试生成场景...")
print("  输出文件夹: /tmp/test_scene_direct")
print("  种子: 0")
print()

infinigen_root = Path("/home/ubuntu/infinigen")
output_folder = "/tmp/test_scene_direct"

cmd = [
    sys.executable,
    '-m', 'infinigen_examples.generate_indoors',
    '--output_folder', output_folder,
    '-s', '0',
    '-g', 'base', 'disable/no_objects',
    '-t', 'coarse'
]

print(f"执行命令: {' '.join(cmd)}")
print()

try:
    result = subprocess.run(
        cmd,
        cwd=str(infinigen_root),
        capture_output=True,
        text=True,
        timeout=300  # 5分钟超时
    )
    
    if result.returncode == 0:
        print("✓ 场景生成成功！")
        print()
        print("检查输出文件:")
        output_path = Path(output_folder)
        if output_path.exists():
            blend_files = list(output_path.rglob("*.blend"))
            if blend_files:
                print(f"  找到 {len(blend_files)} 个场景文件:")
                for f in blend_files[:5]:
                    print(f"    - {f}")
            else:
                print("  未找到 .blend 文件")
                print(f"  输出目录内容: {list(output_path.iterdir())}")
        else:
            print(f"  输出目录不存在: {output_folder}")
    else:
        print("✗ 场景生成失败")
        print()
        print("错误输出:")
        print(result.stderr[:2000] if result.stderr else "无错误输出")
        print()
        print("标准输出:")
        print(result.stdout[-1000:] if result.stdout else "无标准输出")
        
except subprocess.TimeoutExpired:
    print("✗ 场景生成超时（超过5分钟）")
except Exception as e:
    print(f"✗ 执行失败: {e}")

print()
print("="*60)
