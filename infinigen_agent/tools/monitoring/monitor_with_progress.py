#!/usr/bin/env python
"""带进度条的实时测试监控"""
import os
import time
from pathlib import Path
from datetime import datetime
import sys

# 定义所有可能的阶段（基于 pipeline_coarse.csv）
ALL_STAGES = [
    "terrain",
    "sky_lighting",
    "solve_rooms",
    "solve_large",
    "pose_cameras",
    "animate_cameras",
    "populate_intermediate_pholders",
    "solve_medium",
    "solve_small",
    "populate_assets",
    "floating_objs",
    "room_doors",
    "room_windows",
    "room_stairs",
    "skirting_floor",
    "skirting_ceiling",
    "room_pillars",
    "room_walls",
    "room_floors",
    "room_ceilings",
    "lights_off",
    "invisible_room_ceilings",
    "overhead_cam",
    "hide_other_rooms",
    "fancy_clouds",
    "grass",
    "rocks",
    "nature_backdrop",
]

def get_latest_test_dir():
    """获取最新的测试目录"""
    outputs_dir = Path("/home/ubuntu/infinigen/outputs")
    test_dirs = list(outputs_dir.glob("test_langchain_*"))
    if not test_dirs:
        return None
    return max(test_dirs, key=lambda p: p.stat().st_mtime)

def read_pipeline_progress(test_dir):
    """读取 pipeline 进度"""
    pipeline_file = test_dir / "pipeline_coarse.csv"
    
    if not pipeline_file.exists():
        return None, []
    
    completed_stages = []
    try:
        with open(pipeline_file, "r") as f:
            lines = f.readlines()
            # 跳过标题行
            for line in lines[1:]:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        stage_name = parts[1].strip()
                        ran = parts[2].strip().lower() == "true"
                        if ran and stage_name:
                            completed_stages.append(stage_name)
        
        # 获取最后一个阶段
        if completed_stages:
            current_stage = completed_stages[-1]
        else:
            current_stage = None
            
        return current_stage, completed_stages
    except Exception as e:
        return None, []

def calculate_progress(completed_stages, all_stages):
    """计算进度百分比"""
    if not all_stages:
        return 0
    
    # 计算已完成阶段数
    completed_count = len(completed_stages)
    total_count = len(all_stages)
    
    # 如果场景文件已生成，说明已完成
    return min(100, int((completed_count / total_count) * 100))

def draw_progress_bar(progress, width=50):
    """绘制进度条"""
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress}%"

def format_time(seconds):
    """格式化时间"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def main():
    print("=" * 80)
    print("🚀 Infinigen 场景生成进度监控（带进度条）")
    print("=" * 80)
    print("按 Ctrl+C 停止监控\n")
    
    last_completed = []
    last_scene_completed = False
    last_render_completed = False
    start_time = None
    last_display_time = 0
    force_display = True  # 强制第一次显示
    
    try:
        while True:
            test_dir = get_latest_test_dir()
            
            if not test_dir:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ 未找到测试目录")
                time.sleep(5)
                continue
            
            # 记录开始时间
            if start_time is None:
                start_time = test_dir.stat().st_mtime
            
            # 读取进度
            current_stage, completed_stages = read_pipeline_progress(test_dir)
            
            # 检查场景文件
            scene_file = test_dir / "scene.blend"
            if not scene_file.exists():
                scene_file = test_dir / "coarse" / "scene.blend"
            
            scene_completed = scene_file.exists()
            
            # 检查渲染
            render_dirs = list(test_dir.glob("frames_render_*"))
            render_completed = len(render_dirs) > 0 and any(
                (list(render_dir.glob("*.png")) + list(render_dir.glob("*.exr"))) 
                for render_dir in render_dirs
            )
            
            # 计算进度
            if scene_completed:
                progress = 100
                stage_name = "✅ 场景生成完成"
            elif current_stage:
                # 根据当前阶段计算进度
                try:
                    stage_index = ALL_STAGES.index(current_stage)
                    progress = int((stage_index + 1) / len(ALL_STAGES) * 90)  # 90% 用于场景生成
                except ValueError:
                    progress = calculate_progress(completed_stages, ALL_STAGES) * 0.9
                stage_name = f"⏳ {current_stage}"
            elif completed_stages:
                # 有已完成阶段但没有当前阶段（可能刚完成某个阶段）
                progress = calculate_progress(completed_stages, ALL_STAGES) * 0.9
                stage_name = f"⏳ {completed_stages[-1]} (已完成)"
            else:
                # 检查是否有 assets 目录来判断是否在初始化
                has_assets = (test_dir / "assets").exists()
                if has_assets:
                    progress = 5  # 初始阶段，约 5%
                    stage_name = "⏳ Terrain 生成中..."
                else:
                    progress = 0
                    stage_name = "⏳ 初始化中..."
            
            # 计算已运行时间
            elapsed = time.time() - start_time
            
            # 检查是否需要刷新显示（有更新、强制显示、或每10秒强制刷新一次）
            current_time = time.time()
            should_display = (
                force_display or
                completed_stages != last_completed or 
                scene_completed != last_scene_completed or
                render_completed != last_render_completed or
                (current_time - last_display_time) >= 10  # 每10秒强制刷新一次
            )
            
            if should_display:
                # 清屏（使用 ANSI 转义码）
                sys.stdout.write("\033[2J\033[H")
                sys.stdout.flush()
                
                print("=" * 80)
                print(f"📁 测试目录: {test_dir.name}")
                print(f"⏰ 开始时间: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🕐 已运行: {format_time(elapsed)}")
                print("=" * 80)
                print()
                
                # 显示进度条
                print(f"📊 总体进度: {draw_progress_bar(progress)}")
                print()
                
                # 显示当前阶段
                print(f"📍 当前阶段: {stage_name}")
                print()
                
                # 显示已完成的关键阶段
                if completed_stages:
                    print("✅ 已完成阶段:")
                    key_stages = ["terrain", "solve_rooms", "populate_assets", "room_walls", "room_floors"]
                    for stage in key_stages:
                        if stage in completed_stages:
                            print(f"   ✓ {stage}")
                    if len(completed_stages) > len(key_stages):
                        print(f"   ... 共 {len(completed_stages)} 个阶段已完成")
                    print()
                
                # 显示场景文件状态
                if scene_completed:
                    size_mb = scene_file.stat().st_size / (1024 * 1024)
                    print(f"✅ 场景文件: {scene_file.name} ({size_mb:.2f} MB)")
                else:
                    print("⏳ 场景文件: 生成中...")
                
                print()
                
                # 显示渲染状态
                if render_completed:
                    render_files = []
                    for render_dir in render_dirs:
                        render_files.extend(list(render_dir.glob("*.png")) + list(render_dir.glob("*.exr")))
                    print(f"✅ 渲染完成: {len(render_files)} 个文件")
                else:
                    print("⏳ 渲染: 等待场景生成完成...")
                
                print()
                print("=" * 80)
                print(f"🔄 实时更新中... (每3秒检查，有更新时显示) | 按 Ctrl+C 停止")
                
                last_completed = completed_stages.copy()
                last_scene_completed = scene_completed
                last_render_completed = render_completed
                last_display_time = current_time
                force_display = False  # 取消强制显示标志
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n监控已停止")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
