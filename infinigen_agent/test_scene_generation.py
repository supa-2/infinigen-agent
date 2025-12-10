#!/usr/bin/env python
"""
测试场景生成和渲染
使用新的默认设置：save_all_passes=False（只保存最终图像，更快，文件更少）
"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from src.scene_generator import SceneGenerator
from src.scene_renderer import SceneRenderer

def test_scene_generation_and_render():
    """测试场景生成和渲染"""
    print("="*60)
    print("测试场景生成和渲染")
    print("="*60)
    
    # 1. 生成场景
    print("\n[1/2] 生成场景...")
    generator = SceneGenerator()
    
    output_folder = "outputs/test_scene_generation"
    seed = 42  # 固定种子以便复现
    
    # 确保输出目录存在
    from pathlib import Path
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    try:
        scene_path = generator.generate_scene(
            output_folder=output_folder,
            seed=seed,
            task="coarse",
            gin_configs=["fast_solve.gin", "singleroom.gin"],
            gin_overrides=[
                "compose_indoors.terrain_enabled=False",
                # 注意：gin 列表参数语法，使用双引号包裹列表元素（与官方命令一致）
                'restrict_solving.restrict_parent_rooms=["Bedroom"]'
            ],
            timeout=600  # 10分钟超时
        )
        
        print(f"✓ 场景生成成功: {scene_path}")
        
    except Exception as e:
        print(f"✗ 场景生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. 渲染场景（使用新的默认设置：save_all_passes=False）
    print("\n[2/2] 渲染场景（默认 save_all_passes=False，只保存最终图像）...")
    
    try:
        renderer = SceneRenderer(str(scene_path))
        
        # 使用默认设置（save_all_passes=False，只保存最终图像）
        output_image = Path(output_folder) / "rendered_image.png"
        png_path = renderer.render_image(str(output_image))
        
        print(f"✓ 渲染成功: {png_path}")
        
        # 检查输出
        if Path(png_path).exists():
            file_size = Path(png_path).stat().st_size / (1024 * 1024)
            print(f"   文件大小: {file_size:.2f} MB")
        
        # 检查是否只保存了最终图像（默认行为）
        frames_dir = Path(output_folder) / "frames"
        if frames_dir.exists():
            # 检查是否有多个通道目录
            channel_dirs = [d for d in frames_dir.iterdir() if d.is_dir()]
            if len(channel_dirs) > 1:
                print(f"⚠ 发现多个通道目录（{len(channel_dirs)} 个），但默认应该只保存 Image 通道")
            else:
                print(f"✓ 只保存了最终图像（符合默认行为）")
        else:
            print("✓ 未找到 frames 目录（只保存了最终图像，符合默认行为）")
        
        print("\n" + "="*60)
        print("✓ 测试完成！")
        print("="*60)
        print(f"场景文件: {scene_path}")
        print(f"渲染图片: {png_path}")
        if frames_dir.exists():
            print(f"所有通道: {frames_dir}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"✗ 渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scene_generation_and_render()
    sys.exit(0 if success else 1)

