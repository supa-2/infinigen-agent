#!/usr/bin/env python
"""
监控渲染进度
"""
import time
import subprocess
from pathlib import Path
from datetime import datetime

INFINIGEN_ROOT = Path("/home/ubuntu/infinigen")
OUTPUT_FOLDER = INFINIGEN_ROOT / "outputs/hello_room/coarse/frames_render"
LOG_FILE = Path("/tmp/render_log.txt")
RENDER_OUTPUT_LOG = Path("/tmp/render_output.log")

def check_process():
    """检查渲染进程"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "generate_indoors.*render"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return [pid for pid in pids if pid]
        return []
    except:
        return []

def check_output_files():
    """检查输出文件"""
    if not OUTPUT_FOLDER.exists():
        return 0, []
    
    png_files = list(OUTPUT_FOLDER.rglob("*.png"))
    json_files = list(OUTPUT_FOLDER.rglob("*.json"))
    
    return len(png_files), png_files[:5]

def check_log():
    """检查日志文件"""
    if RENDER_OUTPUT_LOG.exists():
        try:
            with open(RENDER_OUTPUT_LOG, 'r') as f:
                lines = f.readlines()
                return lines[-10:] if len(lines) > 10 else lines
        except:
            pass
    return []

def main():
    print("="*60)
    print("渲染进度监控")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"输出文件夹: {OUTPUT_FOLDER}")
    print("")
    
    check_count = 0
    last_png_count = 0
    
    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # 检查进程
            processes = check_process()
            is_running = len(processes) > 0
            
            # 检查输出文件
            png_count, sample_files = check_output_files()
            
            # 检查日志
            log_lines = check_log()
            
            # 显示状态
            print(f"\n[{current_time}] 检查 #{check_count}")
            print("-" * 60)
            
            if is_running:
                print(f"✓ 渲染进程运行中 (PID: {', '.join(processes)})")
            else:
                print("○ 未发现渲染进程")
            
            print(f"PNG 文件数: {png_count}")
            
            if png_count > last_png_count:
                print(f"✓ 新增 {png_count - last_png_count} 个文件")
                last_png_count = png_count
            
            if sample_files:
                print("最新文件:")
                for f in sample_files:
                    size_mb = f.stat().st_size / 1024 / 1024
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%H:%M:%S')
                    print(f"  - {f.name} ({size_mb:.2f} MB, {mtime})")
            
            if log_lines:
                print("\n最新日志:")
                for line in log_lines[-3:]:
                    print(f"  {line.rstrip()}")
            
            # 如果进程不在运行且已有文件，可能已完成
            if not is_running and png_count > 0:
                print("\n" + "="*60)
                print("渲染可能已完成")
                print(f"总共生成 {png_count} 个 PNG 文件")
                print("="*60)
                break
            
            # 等待下一次检查
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")
    except Exception as e:
        print(f"\n错误: {e}")

if __name__ == "__main__":
    main()
