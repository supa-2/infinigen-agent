#!/usr/bin/env python
"""
用户输入测试脚本
让用户输入指令，测试完整流程
"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from src.langchain_agent import LangChainInfinigenAgent

def main():
    print("="*60)
    print("Infinigen Agent - 用户输入测试")
    print("="*60)
    print()
    print("请输入您的需求（例如：生成一个北欧风格的卧室）")
    print("或者输入 'quit' 退出")
    print("="*60)
    
    # 创建 LangChain Agent
    try:
        agent = LangChainInfinigenAgent()
        print("✓ LangChain Agent 初始化成功")
    except Exception as e:
        print(f"✗ LangChain Agent 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    while True:
        print("\n" + "="*60)
        user_request = input("请输入您的需求: ").strip()
        
        if user_request.lower() in ['quit', 'exit', 'q']:
            print("退出程序")
            break
        
        if not user_request:
            print("⚠ 请输入有效的需求")
            continue
        
        # 询问输出文件夹
        output_folder = input("输出文件夹（直接回车使用默认 outputs/test_user_input）: ").strip()
        if not output_folder:
            output_folder = "outputs/test_user_input"
        
        # 询问种子（可选）
        seed_input = input("随机种子（直接回车使用随机）: ").strip()
        seed = int(seed_input) if seed_input.isdigit() else 42
        
        print("\n" + "="*60)
        print("开始执行完整流程...")
        print("="*60)
        print(f"用户请求: {user_request}")
        print(f"输出文件夹: {output_folder}")
        print(f"种子: {seed}")
        print("="*60)
        
        try:
            result = agent.process_request(
                user_input=user_request,
                output_folder=output_folder,
                seed=str(seed),
                timeout=600  # 10分钟超时
            )
            
            if result.get("success"):
                print("\n" + "="*60)
                print("✓ 完整流程执行成功！")
                print("="*60)
                print(f"场景文件: {result.get('scene_file', 'N/A')}")
                
                if 'rendered_image' in result:
                    image_path = Path(result['rendered_image'])
                    if image_path.exists():
                        file_size = image_path.stat().st_size / (1024 * 1024)
                        print(f"渲染图片: {result['rendered_image']}")
                        print(f"  文件大小: {file_size:.2f} MB")
                
                print(f"应用的颜色数: {result.get('colors_applied', 0)}")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("✗ 执行失败")
                print("="*60)
                print(f"错误: {result.get('error', 'N/A')}")
                print(f"消息: {result.get('message', 'N/A')}")
                if result.get('suggestion'):
                    print(f"建议: {result.get('suggestion')}")
                print("="*60)
            
        except KeyboardInterrupt:
            print("\n\n⚠ 用户中断")
            break
        except Exception as e:
            print(f"\n✗ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            print("\n可以继续输入新的需求，或输入 'quit' 退出")

if __name__ == "__main__":
    main()

