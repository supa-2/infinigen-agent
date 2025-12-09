#!/usr/bin/env python3
"""
测试室内场景生成
"""
import subprocess
import sys
from pathlib import Path

def test_indoor_generation():
    """测试室内场景生成"""
    print("="*60)
    print("测试室内场景生成")
    print("="*60)
    
    # 检查依赖
    print("\n[1] 检查依赖...")
    try:
        import yaml
        print("  ✓ yaml 模块已安装")
    except ImportError:
        print("  ✗ yaml 模块未安装")
        print("  请运行: pip install pyyaml")
        return False
    
    try:
        import bpy
        print(f"  ✓ bpy 模块已安装 (版本: {bpy.app.version_string})")
    except ImportError:
        print("  ✗ bpy 模块未安装")
        return False
    
    # 测试导入
    print("\n[2] 测试模块导入...")
    try:
        from infinigen.core.constraints.example_solver.solve import Solver
        print("  ✓ Solver 导入成功")
    except Exception as e:
        print(f"  ✗ Solver 导入失败: {e}")
        return False
    
    # 运行生成命令
    print("\n[3] 运行场景生成（测试模式）...")
    output_folder = "/tmp/test_indoor_check"
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable,
        '-m', 'infinigen_examples.generate_indoors',
        '--output_folder', output_folder,
        '-s', '0',
        '-g', 'base', 'disable/no_objects',
        '-t', 'coarse'
    ]
    
    print(f"  命令: {' '.join(cmd)}")
    print(f"  输出目录: {output_folder}")
    print("  注意: 这可能需要几分钟...")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("  ✓ 场景生成成功！")
            # 检查输出文件
            blend_files = list(Path(output_folder).rglob("*.blend"))
            if blend_files:
                print(f"  ✓ 找到 {len(blend_files)} 个场景文件")
                for f in blend_files[:3]:
                    print(f"    - {f}")
            else:
                print("  ⚠ 未找到 .blend 文件")
            return True
        else:
            print(f"  ✗ 场景生成失败 (退出码: {result.returncode})")
            print("  错误输出:")
            print(result.stderr[:1000])
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠ 场景生成超时（可能需要更长时间）")
        return False
    except Exception as e:
        print(f"  ✗ 运行失败: {e}")
        return False

if __name__ == "__main__":
    success = test_indoor_generation()
    sys.exit(0 if success else 1)
