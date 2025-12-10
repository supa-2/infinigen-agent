#!/usr/bin/env python
"""
测试 Infinigen Agent 完整流程
包括：场景生成 → 颜色应用 → 渲染图片（使用新的默认设置：只保存最终图像）
"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import InfinigenAgent

def test_agent_full_flow():
    """测试 agent 完整流程"""
    print("="*60)
    print("测试 Infinigen Agent 完整流程")
    print("="*60)
    print("流程：场景生成 → 颜色应用 → 渲染图片（只保存最终图像）")
    print("="*60)
    
    # 创建 agent
    print("\n[初始化] 创建 Infinigen Agent...")
    try:
        agent = InfinigenAgent()
        if not agent.scene_generator:
            print("✗ 场景生成器未初始化，无法测试完整流程")
            print("  请确保 Infinigen 根目录正确")
            return False
        print("✓ Agent 初始化成功")
    except Exception as e:
        print(f"✗ Agent 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试参数
    user_request = "生成一个北欧风格的卧室，使用浅灰色和白色"
    output_folder = "outputs/test_agent_full_flow"
    seed = 42  # 固定种子以便复现
    
    # 确保输出目录存在
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[参数]")
    print(f"  用户请求: {user_request}")
    print(f"  输出文件夹: {output_folder}")
    print(f"  种子: {seed}")
    
    # 执行完整流程
    print("\n[执行] 开始完整流程...")
    try:
        results = agent.process_request_with_auto_generate(
            user_request=user_request,
            output_folder=output_folder,
            seed=seed,
            generate_timeout=600,  # 10分钟超时
            render_image=True,  # 渲染图片（默认只保存最终图像）
            render_video=False,
            resolution=None  # 使用场景默认分辨率
        )
        
        print("\n" + "="*60)
        print("✓ 完整流程执行成功！")
        print("="*60)
        print(f"生成的场景: {results.get('generated_scene', 'N/A')}")
        print(f"带颜色的场景: {results.get('colored_scene', 'N/A')}")
        
        if 'image' in results:
            image_path = Path(results['image'])
            if image_path.exists():
                file_size = image_path.stat().st_size / (1024 * 1024)
                print(f"渲染图片: {results['image']}")
                print(f"  文件大小: {file_size:.2f} MB")
                print(f"  ✓ 图片已生成（只保存最终图像，符合默认行为）")
            else:
                print(f"⚠ 图片路径不存在: {results['image']}")
        
        # 检查是否只保存了最终图像（验证默认行为）
        output_path = Path(output_folder)
        frames_dir = output_path / "frames"
        if frames_dir.exists():
            channel_dirs = [d for d in frames_dir.iterdir() if d.is_dir()]
            if len(channel_dirs) > 1:
                print(f"\n⚠ 发现多个通道目录（{len(channel_dirs)} 个）")
                print(f"  通道列表: {', '.join([d.name for d in channel_dirs[:5]])}...")
                print(f"  但默认应该只保存 Image 通道")
            else:
                print(f"\n✓ 验证：只保存了最终图像（符合默认行为）")
        else:
            print(f"\n✓ 验证：未找到 frames 目录（只保存了最终图像，符合默认行为）")
        
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ 完整流程执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_full_flow()
    sys.exit(0 if success else 1)

