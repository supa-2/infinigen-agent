#!/usr/bin/env python
"""详细监控测试进度和时间"""
from pathlib import Path
from datetime import datetime
import time

def get_test_progress():
    """获取测试进度信息"""
    outputs_dir = Path("/home/ubuntu/infinigen/outputs")
    test_dirs = list(outputs_dir.glob("test_langchain_*"))
    
    if not test_dirs:
        return None
    
    latest_dir = max(test_dirs, key=lambda p: p.stat().st_mtime)
    
    info = {
        "dir": latest_dir,
        "start_time": latest_dir.stat().st_mtime,
        "current_time": time.time(),
        "scene_file": None,
        "pipeline_file": None,
        "has_assets": False,
        "has_furniture": False
    }
    
    # 检查场景文件
    scene_file = latest_dir / "scene.blend"
    if not scene_file.exists():
        scene_file = latest_dir / "coarse" / "scene.blend"
    
    if scene_file.exists():
        info["scene_file"] = scene_file
        info["scene_time"] = scene_file.stat().st_mtime
    
    # 检查 pipeline 文件
    pipeline_file = latest_dir / "pipeline_coarse.csv"
    if pipeline_file.exists():
        info["pipeline_file"] = pipeline_file
    
    # 检查 assets
    if (latest_dir / "assets").exists():
        info["has_assets"] = True
    
    # 检查是否有家具（通过检查 solve_state.json 或对象数量）
    solve_state = latest_dir / "solve_state.json"
    if solve_state.exists():
        info["has_furniture"] = True
    
    return info

def format_time(seconds):
    """格式化时间"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}分{secs}秒"

def main():
    print("=" * 70)
    print("测试进度详细监控")
    print("=" * 70)
    print()
    
    # 参考时间（基于之前的测试）
    # 无家具场景生成：约 4-5 分钟
    # 有家具场景生成：预计 8-15 分钟（根据家具数量和复杂度）
    
    last_progress = None
    try:
        while True:
            info = get_test_progress()
            
            if not info:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ 未找到测试目录")
                time.sleep(5)
                continue
            
            elapsed = info["current_time"] - info["start_time"]
            
            # 检查是否有更新
            if info != last_progress:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📁 {info['dir'].name}")
                print(f"   开始时间: {datetime.fromtimestamp(info['start_time']).strftime('%H:%M:%S')}")
                print(f"   已运行: {format_time(elapsed)}")
                print()
                
                # 显示阶段
                if info["scene_file"]:
                    scene_elapsed = info["scene_time"] - info["start_time"]
                    print(f"   ✅ 场景生成完成！")
                    print(f"      耗时: {format_time(scene_elapsed)}")
                    print(f"      文件: {info['scene_file'].name}")
                    size_mb = info["scene_file"].stat().st_size / (1024 * 1024)
                    print(f"      大小: {size_mb:.2f} MB")
                elif info["pipeline_file"]:
                    # 读取 pipeline 文件，查看当前阶段
                    try:
                        with open(info["pipeline_file"], "r") as f:
                            lines = f.readlines()
                            if len(lines) > 1:
                                last_line = lines[-1].strip()
                                if last_line:
                                    parts = last_line.split(",")
                                    if len(parts) > 1:
                                        stage_name = parts[1] if len(parts) > 1 else "unknown"
                                        print(f"   ⏳ 当前阶段: {stage_name}")
                    except:
                        pass
                    print(f"   ⏳ 场景生成中...")
                elif info["has_assets"]:
                    print(f"   ⏳ 阶段: Terrain 已完成，正在生成室内场景...")
                else:
                    print(f"   ⏳ 阶段: 初始化中...")
                
                print()
                
                # 时间估算
                if not info["scene_file"]:
                    print("   ⏱️  时间估算:")
                    print("      - 无家具场景: 约 4-5 分钟")
                    print("      - 有家具场景: 约 8-15 分钟（当前配置）")
                    if elapsed > 15 * 60:
                        print("      ⚠️  已超过预期时间，可能遇到问题")
                    elif elapsed > 10 * 60:
                        print("      ⚠️  时间较长，请耐心等待...")
                    elif elapsed > 5 * 60:
                        print("      ✓ 正常进度范围内")
                    else:
                        print("      ✓ 刚开始，正常")
                    print()
                
                last_progress = info
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")

if __name__ == "__main__":
    main()
