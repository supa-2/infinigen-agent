#!/usr/bin/env python
"""实时监控场景生成测试进度"""
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

def monitor_scene_gen():
    """持续监控场景生成进度"""
    output_dir = Path("/home/ubuntu/infinigen/outputs/test_scene_generation")
    
    print("=" * 70)
    print("场景生成测试 - 实时监控")
    print("=" * 70)
    print(f"输出目录: {output_dir}")
    print("按 Ctrl+C 退出监控\n")
    
    last_file_count = 0
    start_time = datetime.now()
    
    try:
        while True:
            current_time = datetime.now()
            elapsed = current_time - start_time
            
            # 检查进程是否还在运行
            import subprocess
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "generate_indoors"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print("\n⚠ 场景生成进程已结束")
                    break
            except Exception:
                pass
            
            # 检查输出目录
            if output_dir.exists():
                # 统计文件
                all_files = list(output_dir.rglob("*"))
                files = [f for f in all_files if f.is_file()]
                dirs = [d for d in all_files if d.is_dir()]
                
                current_file_count = len(files)
                
                # 检查是否有新文件
                if current_file_count > last_file_count:
                    print(f"\n[{elapsed}] 📁 发现新文件: {current_file_count} 个文件, {len(dirs)} 个目录")
                
                # 检查关键文件
                coarse_dir = output_dir / "coarse"
                scene_file = coarse_dir / "scene.blend" if coarse_dir.exists() else None
                
                if scene_file and scene_file.exists():
                    size_mb = scene_file.stat().st_size / (1024 * 1024)
                    mtime = datetime.fromtimestamp(scene_file.stat().st_mtime)
                    print(f"\n✅ 场景文件已生成!")
                    print(f"   路径: {scene_file}")
                    print(f"   大小: {size_mb:.2f} MB")
                    print(f"   时间: {mtime.strftime('%H:%M:%S')}")
                    print("\n场景生成完成！可以进行渲染了。")
                    break
                
                # 显示当前状态
                sys.stdout.write(f"\r[{elapsed}] ⏳ 正在生成... ({current_file_count} 文件, {len(dirs)} 目录) - {current_time.strftime('%H:%M:%S')}")
                sys.stdout.flush()
                
                last_file_count = current_file_count
            else:
                sys.stdout.write(f"\r[{elapsed}] ⏳ 等待输出目录创建...")
                sys.stdout.flush()
            
            time.sleep(5)  # 每5秒检查一次
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")
    except Exception as e:
        print(f"\n\n错误: {e}")

if __name__ == "__main__":
    monitor_scene_gen()

