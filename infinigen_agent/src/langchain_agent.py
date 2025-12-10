"""
基于 LangChain 的完备 Agent 系统
使用 GLM4.6 验证输入，qwen2.5-7b-infinigen 生成颜色，Infinigen 生成场景
"""
import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import logging

# 添加项目根目录到路径（确保可以从任何位置运行）
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # infinigen_agent 目录
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.scene_generator import SceneGenerator
from src.scene_color_applier import SceneColorApplier
from src.scene_renderer import SceneRenderer
from src.color_parser import ColorParser
from src.procedural_furniture_generator import ProceduralFurnitureGenerator
from src.room_type_detector import detect_room_type
import numpy as np

# 导入 vLLM API 配置
try:
    from config.api_config import (
        VLLM_API_URL,
        VLLM_API_KEY,
        DEFAULT_MODEL as VLLM_DEFAULT_MODEL,
        USE_V1_PATH,
        VLLM_API_URL_NO_V1
    )
except ImportError:
    # 如果配置文件不存在，使用默认值
    VLLM_API_BASE_URL = "https://service.thuarchdog.com:58889"
    VLLM_API_URL = f"{VLLM_API_BASE_URL}/v1"
    VLLM_API_URL_NO_V1 = VLLM_API_BASE_URL
    VLLM_API_KEY = "sk-Z0MdU0NAXCmiwYF_3io5kXtwl8cxHEtGciRtopREtFsDMXLMkjHxLGlBTX8"
    VLLM_DEFAULT_MODEL = "Qwen2.5-7B-infinigen"
    USE_V1_PATH = True

logger = logging.getLogger(__name__)


class LangChainInfinigenAgent:
    """基于 LangChain 的 Infinigen Agent"""
    
    def __init__(
        self,
        infinigen_root: Optional[str] = None,
        glm_api_key: str = "sk-QEBvsYNQh6pvLotdR4DK1w",
        glm_base_url: str = "https://llmapi.paratera.com",
        qwen_model_name: Optional[str] = None,
        vllm_api_url: Optional[str] = None,
        vllm_api_key: Optional[str] = None
    ):
        """
        初始化 LangChain Agent
        
        Args:
            infinigen_root: Infinigen 根目录路径
            glm_api_key: GLM4.6 API Key（用于输入验证）
            glm_base_url: GLM4.6 API Base URL
            qwen_model_name: Qwen 模型名称（vLLM 部署的模型，默认从配置文件读取）
            vllm_api_url: vLLM API URL（默认从配置文件读取）
            vllm_api_key: vLLM API Key（默认从配置文件读取）
        """
        self.infinigen_root = infinigen_root or self._detect_infinigen_root()
        
        # 初始化 GLM4.6 模型（用于输入验证）
        # 注意：根据API错误信息，需要使用允许的模型名称，如 GLM-4.6, GLM-4-Plus, GLM-4-Flash 等
        self.glm_llm = ChatOpenAI(
            model="GLM-4.6",  # 使用允许的模型名称
            api_key=glm_api_key,
            base_url=glm_base_url,
            temperature=0.3
        )
        
        # 初始化 Qwen 模型（用于颜色生成）
        # 使用 vLLM 部署的 API（独立于 GLM API）
        qwen_model = qwen_model_name or VLLM_DEFAULT_MODEL
        
        # 根据配置选择正确的 API URL
        if vllm_api_url:
            qwen_api_url = vllm_api_url
        else:
            qwen_api_url = VLLM_API_URL if USE_V1_PATH else VLLM_API_URL_NO_V1
        
        qwen_api_key = vllm_api_key or VLLM_API_KEY
        
        logger.info(f"初始化 Qwen 模型: {qwen_model}")
        logger.info(f"vLLM API URL: {qwen_api_url}")
        
        self.qwen_llm = ChatOpenAI(
            model=qwen_model,
            api_key=qwen_api_key,
            base_url=qwen_api_url,
            temperature=0.7
        )
        
        # 初始化 Infinigen 组件
        self.scene_generator = SceneGenerator(infinigen_root=self.infinigen_root)
        self.color_parser = ColorParser()
        self.scene_applier = None
        self.scene_renderer = None
        self.procedural_generator = None  # 延迟初始化（需要在 Blender 环境中）
        
        logger.info("LangChain Infinigen Agent 初始化完成")
    
    def _detect_infinigen_root(self) -> Path:
        """自动检测 Infinigen 根目录"""
        current_dir = Path(__file__).parent.parent
        if current_dir.name == 'infinigen_agent':
            return current_dir.parent
        return Path('/home/ubuntu/infinigen')
    
    def validate_user_input(self, user_input: str) -> tuple[bool, str]:
        """
        使用 GLM4.6 验证用户输入是否合理
        
        Args:
            user_input: 用户输入
            
        Returns:
            (is_valid, message) - 是否合理，消息
        """
        messages = [
            SystemMessage(content="""你是一个场景生成助手。你的任务是判断用户输入是否合理。

合理的输入应该：
1. 描述一个室内场景（如卧室、客厅、厨房等）
2. 可以包含家具和颜色要求
3. 要求明确、可实现

不合理的输入包括：
1. 完全无关的内容
2. 过于模糊或无法理解
3. 包含不合理的物理要求

请用中文回复，格式：
- 如果合理：回复"合理：[简要说明]"
- 如果不合理：回复"不合理：[原因，并建议如何修改]"
"""),
            HumanMessage(content=user_input)
        ]
        
        try:
            response = self.glm_llm.invoke(messages)
            result_text = response.content.strip()
            
            is_valid = result_text.startswith("合理")
            return is_valid, result_text
            
        except Exception as e:
            logger.error(f"GLM4.6 验证失败: {e}")
            # 默认认为合理，继续处理
            return True, f"验证服务异常，继续处理: {str(e)}"
    
    def generate_furniture_colors(self, user_input: str) -> str:
        """
        使用 Qwen 模型生成家具颜色方案
        
        Args:
            user_input: 用户输入
            
        Returns:
            颜色方案 JSON 字符串
        """
        messages = [
            SystemMessage(content="""你是一个室内设计助手。根据用户的描述，生成家具颜色方案。

请分析用户输入，提取出：
1. 场景类型（卧室、客厅、厨房等）
2. 提到的家具及其颜色
3. 整体风格（如北欧风、现代风等）

如果没有明确指定颜色，请根据场景类型和风格推荐合适的颜色。

请以 JSON 格式返回，格式：
{
    "scene_type": "场景类型",
    "style": "风格",
    "furniture_colors": [
        {
            "furniture": "家具名称",
            "color": "颜色名称",
            "rgb": [R, G, B],
            "hex": "#RRGGBB"
        }
    ]
}

只返回 JSON，不要其他文字。
"""),
            HumanMessage(content=user_input)
        ]
        
        try:
            response = self.qwen_llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Qwen 颜色生成失败: {e}")
            raise
    
    def process_request(
        self,
        user_input: str,
        output_folder: str,
        seed: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        处理用户请求的完整流程
        
        Args:
            user_input: 用户输入
            output_folder: 输出文件夹
            seed: 随机种子
            timeout: 超时时间
            
        Returns:
            包含场景文件、渲染图片等信息的字典
        """
        print("=" * 60)
        print("LangChain Infinigen Agent - 处理请求")
        print("=" * 60)
        
        # 步骤1: 验证用户输入
        print("\n步骤1: 验证用户输入...")
        is_valid, validation_message = self.validate_user_input(user_input)
        
        if not is_valid:
            print(f"✗ 输入不合理: {validation_message}")
            return {
                "success": False,
                "error": "输入不合理",
                "message": validation_message,
                "suggestion": "请重新输入一个合理的场景描述"
            }
        
        print(f"✓ 输入验证通过: {validation_message}")
        
        # 步骤2: 并行执行 - 生成颜色方案和场景
        print("\n步骤2: 并行生成颜色方案和场景...")
        
        # 2.1 生成颜色方案
        print("  2.1 生成家具颜色方案...")
        try:
            color_scheme_json = self.generate_furniture_colors(user_input)
            print(f"  ✓ 颜色方案生成成功")
            print(f"  {color_scheme_json[:200]}...")  # 显示前200字符
        except Exception as e:
            print(f"  ✗ 颜色方案生成失败: {e}")
            return {
                "success": False,
                "error": "颜色生成失败",
                "message": str(e)
            }
        
        # 2.2 生成场景（并行）
        print("  2.2 生成场景（使用 Infinigen 原生命令）...")
        print("      ⚡ 使用超快配置（ultra_fast_solve.gin + singleroom.gin）")
        print("      预计时间: 5-10 分钟（vs fast_solve 8-13 分钟，默认 50+ 分钟）")
        try:
            # 检测房间类型
            room_type = detect_room_type(user_input)
            
            # 默认使用超快配置（ultra_fast_solve.gin 比 fast_solve.gin 更快）
            # ultra_fast_solve.gin: FloorPlanSolver 参数更小（10 vs 25），求解步数相同
            gin_configs = ['ultra_fast_solve.gin', 'singleroom.gin']
            gin_overrides = ['compose_indoors.terrain_enabled=False']
            
            # 如果检测到房间类型，添加到覆盖中
            # 注意：官方文档格式是 restrict_solving.restrict_parent_rooms=\[\"RoomType\"\]
            # 在 shell 中，\[ 会被解释为 [，\" 会被解释为 "，所以最终传递给 gin 的是 ["RoomType"]
            # 在 Python 字符串中，我们需要使用 \\[ 和 \\" 来表示 shell 中的 \[ 和 \"
            # 但是 shell 解释 \" 时可能会丢失引号，所以我们需要使用不同的格式
            # 实际上，gin 解析器期望的格式是 ["RoomType"]，而不是 [RoomType]
            # 让我们直接使用官方文档中的格式，让 shell 正确解释
            if room_type:
                # 格式：restrict_solving.restrict_parent_rooms=\[\"RoomType\"\]
                # 在 Python 字符串中：\\[ 表示 shell 中的 \[，\\" 表示 shell 中的 \"
                gin_overrides.append(f'restrict_solving.restrict_parent_rooms=\\[\\"{room_type}\\"\\]')
                print(f"      ✓ 检测到房间类型: {room_type}")
            
            scene_file = self.scene_generator.generate_scene(
                output_folder=output_folder,
                seed=seed,
                task="coarse",
                gin_configs=gin_configs,
                gin_overrides=gin_overrides,
                timeout=timeout
            )
            
            # 确保 scene_file 是 Path 对象
            from pathlib import Path
            scene_file = Path(scene_file)
            
            print(f"  ✓ 场景生成命令执行完成")
            print(f"  📁 返回的场景文件路径: {scene_file}")
            
            # 如果返回的是目录，尝试查找场景文件
            if scene_file.is_dir():
                print(f"  ⚠ 返回的是目录，正在查找场景文件...")
                possible_scene = scene_file / "scene.blend"
                if possible_scene.exists():
                    scene_file = possible_scene
                    print(f"  ✓ 找到场景文件: {scene_file}")
                else:
                    # 递归查找
                    blend_files = list(scene_file.rglob("*.blend"))
                    if blend_files:
                        scene_file = blend_files[0]
                        print(f"  ✓ 找到场景文件: {scene_file}")
                    else:
                        raise FileNotFoundError(f"在目录中未找到场景文件: {scene_file}")
            
            # 确认场景文件存在且有效
            if not scene_file.exists():
                raise FileNotFoundError(f"场景文件不存在: {scene_file}")
            
            file_size = scene_file.stat().st_size
            if file_size < 1024:
                raise ValueError(f"场景文件大小异常（可能未完全生成）: {file_size} 字节")
            
            print(f"  ✓ 场景文件验证通过: {scene_file} (大小: {file_size / (1024*1024):.2f} MB)")
            print(f"  → 准备继续执行后续步骤（应用颜色和渲染）...")
        except Exception as e:
            print(f"  ✗ 场景生成失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": "场景生成失败",
                "message": str(e)
            }
        
        # 步骤3: 应用颜色到场景
        print(f"\n{'='*60}")
        print("步骤3: 应用颜色到场景")
        print(f"{'='*60}")
        try:
            # 解析颜色方案
            import json
            colors = []
            
            # 尝试解析 JSON
            try:
                # 先尝试直接解析 JSON
                color_data = json.loads(color_scheme_json)
                colors = self.color_parser.parse_colors_from_dict(color_data)
            except json.JSONDecodeError:
                # 如果 JSON 解析失败，尝试提取 JSON 部分
                import re
                json_match = re.search(r'\{.*\}', color_scheme_json, re.DOTALL)
                if json_match:
                    try:
                        color_data = json.loads(json_match.group())
                        colors = self.color_parser.parse_colors_from_dict(color_data)
                    except:
                        pass
            
            # 如果还是失败，使用通用解析方法
            if not colors:
                colors = self.color_parser.parse_colors(color_scheme_json)
            
            if not colors:
                raise ValueError("无法解析颜色方案，请检查模型输出格式")
            
            print(f"  ✓ 解析到 {len(colors)} 个颜色配置")
            
            # 加载场景并应用颜色
            print(f"  正在加载场景文件: {scene_file}")
            print("  ⚠ 如果场景文件很大，这可能需要几分钟...")
            self.scene_applier = SceneColorApplier(str(scene_file))
            
            # 初始化程序化生成器（用于生成缺失的家具）
            print("  正在初始化程序化生成器...")
            self.procedural_generator = ProceduralFurnitureGenerator(
                factory_seed=np.random.randint(1, 1e9),
                coarse=False
            )
            print("  ✓ 程序化生成器初始化完成")
            
            # 分类家具：支持程序化生成 vs 不支持
            procedural_supported = []
            procedural_unsupported = []
            
            for color in colors:
                furniture_type = color.furniture_type.lower()
                if self.procedural_generator.is_furniture_type_supported(furniture_type):
                    procedural_supported.append(color)
                else:
                    procedural_unsupported.append(color)
            
            # 步骤3.1: 使用程序化生成器生成家具并应用颜色
            if procedural_supported:
                print(f"\n  3.1 使用程序化生成器生成 {len(procedural_supported)} 个家具类型:")
                for color in procedural_supported:
                    furniture_type = color.furniture_type.lower()
                    
                    # 生成家具（默认位置在原点）
                    obj = self.procedural_generator.generate_furniture(
                        furniture_type=furniture_type,
                        location=(0, 0, 0),
                        color=color.rgb if color.rgb else None
                    )
                    
                    if obj:
                        if color.rgb:
                            print(f"    ✓ {furniture_type}: 已生成（生成时已应用颜色 {color.rgb}）")
                        else:
                            self.scene_applier.apply_color_to_object(obj, color)
                            print(f"    ✓ {furniture_type}: 已生成并应用颜色")
                    else:
                        print(f"    ✗ {furniture_type}: 生成失败")
            
            # 步骤3.2: 在场景中查找已有对象并应用颜色
            if procedural_unsupported:
                print(f"\n  3.2 在场景中查找 {len(procedural_unsupported)} 个已有对象并应用颜色:")
                for color in procedural_unsupported:
                    objects = self.scene_applier.find_objects_by_name([color.furniture_type])
                    if objects:
                        for obj in objects:
                            self.scene_applier.apply_color_to_object(obj, color)
                        print(f"    ✓ {color.furniture_type}: 找到 {len(objects)} 个对象并应用颜色 {color.color_name}")
                    else:
                        print(f"    ⚠ {color.furniture_type}: 场景中未找到该家具（不支持程序化生成）")
            
            # 保存场景（替换原文件，不生成新文件）
            self.scene_applier.save_scene(str(scene_file))
            print(f"\n  ✓ 颜色已应用到场景并保存: {scene_file}")
            
        except Exception as e:
            print(f"  ✗ 应用颜色失败: {e}")
            import traceback
            traceback.print_exc()
            print(f"  ⚠ 颜色应用失败，但将继续渲染场景（使用原始颜色）")
            # 不返回错误，继续执行渲染步骤
        
        # 步骤4: 渲染图片（无论颜色应用是否成功，都会渲染）
        print("\n步骤4: 渲染场景图片...")
        try:
            self.scene_renderer = SceneRenderer(str(scene_file))
            output_image = Path(scene_file).parent / "rendered_image.png"
            
            # 只渲染单张图片（默认只保存最终图像）
            rendered_image = self.scene_renderer.render_image(
                output_path=str(output_image),
                resolution=(1920, 1080),
                save_all_passes=False  # 只保存最终图像，更快，文件更少
            )
            
            print(f"  ✓ 图片渲染成功: {rendered_image}")
            
        except Exception as e:
            print(f"  ✗ 渲染失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": "渲染失败",
                "message": str(e),
                "scene_file": str(scene_file)
            }
        
        # 返回结果
        print("\n" + "=" * 60)
        print("✓ 处理完成！")
        print("=" * 60)
        
        return {
            "success": True,
            "user_input": user_input,
            "scene_file": str(scene_file),
            "rendered_image": str(rendered_image),
            "color_scheme": color_scheme_json,
            "colors_applied": len(colors) if colors else 0
        }
    
    def process_existing_scene(
        self,
        scene_file: str,
        user_input: Optional[str] = None,
        color_scheme_json: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理已存在的场景文件（跳过场景生成步骤）
        
        Args:
            scene_file: 已生成的场景文件路径（.blend 文件）
            user_input: 用户输入（可选，用于生成颜色方案）
            color_scheme_json: 颜色方案 JSON（可选，如果提供则直接使用）
            
        Returns:
            包含场景文件、渲染图片等信息的字典
        """
        print("=" * 60)
        print("LangChain Infinigen Agent - 处理已有场景")
        print("=" * 60)
        print(f"场景文件: {scene_file}")
        
        scene_path = Path(scene_file)
        if not scene_path.exists():
            return {
                "success": False,
                "error": "场景文件不存在",
                "message": f"文件不存在: {scene_file}"
            }
        
        # 步骤1: 生成颜色方案（如果需要）
        if color_scheme_json is None and user_input:
            print("\n步骤1: 生成颜色方案...")
            try:
                color_scheme_json = self.generate_furniture_colors(user_input)
                print(f"  ✓ 颜色方案生成成功")
            except Exception as e:
                print(f"  ✗ 颜色方案生成失败: {e}")
                color_scheme_json = None
        
        # 步骤2: 应用颜色到场景（如果提供了颜色方案）
        if color_scheme_json:
            print("\n步骤2: 应用颜色到场景...")
            try:
                import json
                colors = []
                
                try:
                    color_data = json.loads(color_scheme_json)
                    colors = self.color_parser.parse_colors_from_dict(color_data)
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'\{.*\}', color_scheme_json, re.DOTALL)
                    if json_match:
                        try:
                            color_data = json.loads(json_match.group())
                            colors = self.color_parser.parse_colors_from_dict(color_data)
                        except:
                            pass
                
                if not colors:
                    colors = self.color_parser.parse_colors(color_scheme_json)
                
                if colors:
                    print(f"  ✓ 解析到 {len(colors)} 个颜色配置")
                    print(f"  正在加载场景文件: {scene_file}")
                    self.scene_applier = SceneColorApplier(str(scene_file))
                    
                    for color in colors:
                        objects = self.scene_applier.find_objects_by_name([color.furniture_type])
                        if objects:
                            for obj in objects:
                                self.scene_applier.apply_color_to_object(obj, color)
                            print(f"    ✓ {color.furniture_type}: 找到 {len(objects)} 个对象并应用颜色")
                    
                    self.scene_applier.save_scene(str(scene_file))
                    print(f"  ✓ 颜色已应用到场景并保存")
                else:
                    print(f"  ⚠ 无法解析颜色方案，跳过颜色应用")
            except Exception as e:
                print(f"  ✗ 应用颜色失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 步骤3: 渲染图片
        print("\n步骤3: 渲染场景图片...")
        try:
            self.scene_renderer = SceneRenderer(str(scene_file))
            output_image = scene_path.parent / "rendered_image.png"
            
            rendered_image = self.scene_renderer.render_image(
                output_path=str(output_image),
                resolution=(1920, 1080),
                save_all_passes=False
            )
            
            print(f"  ✓ 图片渲染成功: {rendered_image}")
            
            return {
                "success": True,
                "scene_file": str(scene_file),
                "rendered_image": str(rendered_image),
                "color_scheme": color_scheme_json if color_scheme_json else None
            }
        except Exception as e:
            print(f"  ✗ 渲染失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": "渲染失败",
                "message": str(e),
                "scene_file": str(scene_file)
            }
    
    def interactive_mode(self):
        """交互式模式"""
        print("=" * 60)
        print("LangChain Infinigen Agent - 交互式模式")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print()
        
        while True:
            try:
                user_input = input("请输入场景描述: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理请求
                result = self.process_request(
                    user_input=user_input,
                    output_folder=f"/home/ubuntu/infinigen/outputs/interactive_{int(__import__('time').time())}",
                    timeout=600  # 10分钟超时
                )
                
                if result.get("success"):
                    print(f"\n✓ 成功！")
                    print(f"  场景文件: {result['scene_file']}")
                    print(f"  渲染图片: {result['rendered_image']}")
                else:
                    print(f"\n✗ 失败: {result.get('error')}")
                    print(f"  消息: {result.get('message')}")
                    if result.get('suggestion'):
                        print(f"  建议: {result['suggestion']}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n\n程序被中断")
                break
            except Exception as e:
                print(f"\n✗ 发生错误: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    import sys
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(
        description="LangChain Infinigen Agent - 根据自然语言描述生成、修改和渲染 3D 场景",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互式模式
  python langchain_agent.py
  
  # 命令行模式
  python langchain_agent.py "生成一个北欧风格的卧室"
  
  # 指定输出文件夹和种子
  python langchain_agent.py "生成一个现代风格的客厅" --output-folder outputs/my_scene --seed 42
        """
    )
    
    parser.add_argument(
        "user_input",
        nargs="?",
        help="用户输入的场景描述（如果未提供，进入交互式模式）"
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default=None,
        help="输出文件夹路径（默认: outputs/langchain_<timestamp>）"
    )
    parser.add_argument(
        "--seed",
        type=str,
        default=None,
        help="随机种子（默认: 随机生成）"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="场景生成超时时间（秒，默认: 600）"
    )
    
    args = parser.parse_args()
    
    # 初始化 Agent
    print("=" * 60)
    print("LangChain Infinigen Agent")
    print("=" * 60)
    print("初始化中...")
    
    try:
        agent = LangChainInfinigenAgent()
        print("✓ Agent 初始化成功\n")
    except Exception as e:
        print(f"✗ Agent 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if args.user_input:
        # 命令行模式
        user_input = args.user_input
        
        # 确定输出文件夹
        if args.output_folder:
            output_folder = args.output_folder
        else:
            import time
            timestamp = int(time.time())
            output_folder = f"/home/ubuntu/infinigen/outputs/langchain_{timestamp}"
        
        print(f"用户输入: {user_input}")
        print(f"输出文件夹: {output_folder}")
        if args.seed:
            print(f"种子: {args.seed}")
        print("=" * 60 + "\n")
        
        try:
            result = agent.process_request(
                user_input=user_input,
                output_folder=output_folder,
                seed=args.seed,
                timeout=args.timeout
            )
            
            print("\n" + "=" * 60)
            if result.get("success"):
                print("✓ 成功！")
                print("=" * 60)
                print(f"场景文件: {result['scene_file']}")
                if 'rendered_image' in result:
                    print(f"渲染图片: {result['rendered_image']}")
                print(f"应用颜色数: {result.get('colors_applied', 0)}")
            else:
                print("✗ 失败")
                print("=" * 60)
                print(f"错误: {result.get('error')}")
                print(f"消息: {result.get('message')}")
                if result.get('suggestion'):
                    print(f"建议: {result.get('suggestion')}")
            print("=" * 60)
            
            sys.exit(0 if result.get("success") else 1)
            
        except KeyboardInterrupt:
            print("\n\n⚠ 用户中断")
            sys.exit(130)
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # 交互式模式
        agent.interactive_mode()
