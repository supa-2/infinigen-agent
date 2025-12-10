#!/usr/bin/env python
"""
Infinigen Web API 服务器
提供场景生成、进度查询、文件下载等接口
"""
import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid

# 添加 infinigen_agent 到路径
infinigen_agent_path = Path(__file__).parent.parent / "infinigen_agent"
if not infinigen_agent_path.exists():
    # 备用路径
    infinigen_agent_path = Path("/home/ubuntu/infinigen/infinigen_agent")
sys.path.insert(0, str(infinigen_agent_path))

from src.langchain_agent import LangChainInfinigenAgent

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = Path("/home/ubuntu/infinigen/outputs")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'blend'}

# 存储任务状态
tasks = {}

# 初始化 Agent
print("正在初始化 LangChain Infinigen Agent...")
try:
    agent = LangChainInfinigenAgent(
        infinigen_root="/home/ubuntu/infinigen",
        use_template_pool=True  # 启用模板池
    )
    print("✓ Agent 初始化成功")
except Exception as e:
    print(f"⚠ Agent 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    agent = None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_task_output_dir(task_id):
    """获取任务输出目录"""
    return UPLOAD_FOLDER / f"web_task_{task_id}"


def read_pipeline_progress(output_dir):
    """读取 pipeline 进度"""
    pipeline_file = output_dir / "pipeline_coarse.csv"
    
    if not pipeline_file.exists():
        return None, []
    
    completed_stages = []
    try:
        with open(pipeline_file, "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        stage_name = parts[1].strip()
                        ran = parts[2].strip().lower() == "true"
                        if ran and stage_name:
                            completed_stages.append(stage_name)
        
        current_stage = completed_stages[-1] if completed_stages else None
        return current_stage, completed_stages
    except Exception as e:
        return None, []


ALL_STAGES = [
    "terrain", "sky_lighting", "solve_rooms", "solve_large", "pose_cameras",
    "animate_cameras", "populate_intermediate_pholders", "solve_medium",
    "solve_small", "populate_assets", "floating_objs", "room_doors",
    "room_windows", "room_stairs", "skirting_floor", "skirting_ceiling",
    "room_pillars", "room_walls", "room_floors", "room_ceilings",
    "lights_off", "invisible_room_ceilings", "overhead_cam", "hide_other_rooms",
    "fancy_clouds", "grass", "rocks", "nature_backdrop",
]


def calculate_progress(output_dir):
    """计算任务进度"""
    # 检查场景文件
    scene_file = output_dir / "scene.blend"
    if not scene_file.exists():
        scene_file = output_dir / "coarse" / "scene.blend"
    
    if scene_file.exists():
        # 检查渲染文件
        render_files = list(output_dir.glob("frames/**/*.png")) + list(output_dir.glob("frames/**/*.exr"))
        if render_files:
            return 100, "渲染完成"
        return 95, "场景生成完成，正在渲染"
    
    # 读取 pipeline 进度
    current_stage, completed_stages = read_pipeline_progress(output_dir)
    
    if current_stage:
        try:
            stage_index = ALL_STAGES.index(current_stage)
            progress = int((stage_index + 1) / len(ALL_STAGES) * 90)
        except ValueError:
            progress = int(len(completed_stages) / len(ALL_STAGES) * 90)
        return progress, f"正在执行: {current_stage}"
    elif completed_stages:
        progress = int(len(completed_stages) / len(ALL_STAGES) * 90)
        return progress, f"已完成: {completed_stages[-1]}"
    else:
        if (output_dir / "assets").exists():
            return 5, "初始化中..."
        return 0, "等待开始..."


def generate_scene_task(task_id, user_request, seed=None, mode="template", auto_confirm=False):
    """在后台线程中生成场景"""
    try:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["message"] = "开始生成场景..."
        tasks[task_id]["mode"] = mode
        
        output_dir = get_task_output_dir(task_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用 agent 生成场景
        if agent is None:
            raise Exception("Agent 未初始化")
        
        # 处理 seed 参数
        import random
        if seed is None:
            actual_seed = None  # 让 Agent 自动生成
        else:
            actual_seed = str(seed)
        
        # 调用 Agent 的 process_request 方法
        results = agent.process_request(
            user_input=user_request,
            output_folder=str(output_dir),
            seed=actual_seed,
            timeout=1200,  # 20分钟超时
            mode=mode,
            auto_confirm=auto_confirm
        )
        
        if results.get("success"):
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["message"] = "场景生成完成"
            tasks[task_id]["scene_file"] = str(results.get("scene_file", ""))
            tasks[task_id]["rendered_image"] = str(results.get("rendered_image", ""))
            tasks[task_id]["preview_image"] = str(results.get("preview_image", ""))
            tasks[task_id]["used_template"] = results.get("used_template", False)
            tasks[task_id]["needs_confirmation"] = results.get("needs_confirmation", False)
            tasks[task_id]["mode"] = results.get("mode", mode)
            
            # 如果使用了模板模式，记录颜色方案
            if mode == "template":
                tasks[task_id]["color_scheme"] = results.get("color_scheme", "")
                tasks[task_id]["colors_applied"] = results.get("colors_applied", 0)
        else:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = results.get("message", "生成失败")
            tasks[task_id]["error"] = results.get("error", "未知错误")
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"生成失败: {str(e)}"
        import traceback
        tasks[task_id]["error"] = traceback.format_exc()


@app.route('/api/generate', methods=['POST'])
def generate_scene():
    """生成场景接口"""
    data = request.json
    user_request = data.get('request', '')
    seed = data.get('seed', None)
    mode = data.get('mode', 'template')  # 'template' 或 'generate'
    auto_confirm = data.get('auto_confirm', False)  # 仅用于 generate 模式
    
    if not user_request:
        return jsonify({"error": "请求不能为空"}), 400
    
    if agent is None:
        return jsonify({"error": "Agent 未初始化"}), 500
    
    if mode not in ['template', 'generate']:
        return jsonify({"error": "无效的模式，必须是 'template' 或 'generate'"}), 400
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "message": "任务已创建",
        "created_at": datetime.now().isoformat(),
        "user_request": user_request,
        "seed": seed,
        "mode": mode,
        "auto_confirm": auto_confirm
    }
    
    # 在后台线程中执行
    thread = threading.Thread(
        target=generate_scene_task,
        args=(task_id, user_request, seed, mode, auto_confirm)
    )
    thread.daemon = True
    thread.start()
    
    mode_text = "模板模式" if mode == "template" else "生成模式"
    return jsonify({
        "task_id": task_id,
        "status": "pending",
        "message": f"任务已创建（{mode_text}），正在生成场景...",
        "mode": mode
    })


@app.route('/api/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({"error": "任务不存在"}), 404
    
    task = tasks[task_id]
    output_dir = get_task_output_dir(task_id)
    
    # 计算进度
    if task["status"] == "running":
        progress, message = calculate_progress(output_dir)
        task["progress"] = progress
        task["current_stage"] = message
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "message": task.get("message", ""),
        "progress": task.get("progress", 0),
        "current_stage": task.get("current_stage", ""),
        "created_at": task.get("created_at", ""),
        "user_request": task.get("user_request", "")
    }
    
    # 如果完成，添加文件路径
    if task["status"] == "completed":
        response["scene_file"] = task.get("scene_file", "")
        response["rendered_image"] = task.get("rendered_image", "")
        response["preview_image"] = task.get("preview_image", "")
        response["used_template"] = task.get("used_template", False)
        response["needs_confirmation"] = task.get("needs_confirmation", False)
        response["mode"] = task.get("mode", "template")
        
        # 模板模式特有信息
        if task.get("mode") == "template":
            response["color_scheme"] = task.get("color_scheme", "")
            response["colors_applied"] = task.get("colors_applied", 0)
    
    return jsonify(response)


@app.route('/api/task/<task_id>/image', methods=['GET'])
def get_task_image(task_id):
    """获取任务生成的图片（优先返回精修渲染图，否则返回预览图）"""
    if task_id not in tasks:
        return jsonify({"error": "任务不存在"}), 404
    
    task = tasks[task_id]
    output_dir = get_task_output_dir(task_id)
    
    # 优先查找精修渲染图片
    image_files = list(output_dir.glob("frames/**/*.png")) + list(output_dir.glob("frames/**/*.exr"))
    if not image_files:
        # 尝试直接查找
        image_files = list(output_dir.glob("rendered_image.png")) + list(output_dir.glob("*.png"))
    
    if not image_files:
        # 查找预览图片
        preview_file = output_dir / "preview_image.png"
        if preview_file.exists():
            return send_file(str(preview_file), mimetype='image/png')
    
    if image_files:
        # 返回最新的图片
        latest_image = max(image_files, key=lambda p: p.stat().st_mtime)
        return send_file(str(latest_image), mimetype='image/png')
    
    return jsonify({"error": "图片未找到"}), 404


@app.route('/api/task/<task_id>/preview', methods=['GET'])
def get_task_preview(task_id):
    """获取任务预览图片"""
    if task_id not in tasks:
        return jsonify({"error": "任务不存在"}), 404
    
    task = tasks[task_id]
    output_dir = get_task_output_dir(task_id)
    
    # 查找预览图片
    preview_file = output_dir / "preview_image.png"
    if preview_file.exists():
        return send_file(str(preview_file), mimetype='image/png')
    
    return jsonify({"error": "预览图片未找到"}), 404


@app.route('/api/task/<task_id>/download/<file_type>', methods=['GET'])
def download_file(task_id, file_type):
    """下载场景文件"""
    if task_id not in tasks:
        return jsonify({"error": "任务不存在"}), 404
    
    task = tasks[task_id]
    output_dir = get_task_output_dir(task_id)
    
    if file_type == "scene":
        # 查找场景文件
        scene_file = output_dir / "scene.blend"
        if not scene_file.exists():
            scene_file = output_dir / "coarse" / "scene.blend"
        
        if scene_file.exists():
            return send_file(
                str(scene_file),
                as_attachment=True,
                download_name=f"scene_{task_id}.blend"
            )
    
    elif file_type == "image":
        # 优先查找精修渲染图片
        image_files = list(output_dir.glob("frames/**/*.png")) + list(output_dir.glob("frames/**/*.exr"))
        if not image_files:
            image_files = list(output_dir.glob("rendered_image.png")) + list(output_dir.glob("*.png"))
        
        if image_files:
            latest_image = max(image_files, key=lambda p: p.stat().st_mtime)
            return send_file(
                str(latest_image),
                as_attachment=True,
                download_name=f"rendered_{task_id}.png"
            )
    
    elif file_type == "preview":
        preview_file = output_dir / "preview_image.png"
        if preview_file.exists():
            return send_file(
                str(preview_file),
                as_attachment=True,
                download_name=f"preview_{task_id}.png"
            )
    
    return jsonify({"error": "文件未找到"}), 404


@app.route('/api/task/<task_id>/confirm', methods=['POST'])
def confirm_and_render(task_id):
    """确认并精修渲染场景（用于生成模式）"""
    if task_id not in tasks:
        return jsonify({"error": "任务不存在"}), 404
    
    task = tasks[task_id]
    
    if task.get("mode") != "generate":
        return jsonify({"error": "只有生成模式才能使用此接口"}), 400
    
    if task["status"] != "completed" or not task.get("needs_confirmation"):
        return jsonify({"error": "任务状态不正确"}), 400
    
    if agent is None:
        return jsonify({"error": "Agent 未初始化"}), 500
    
    # 在后台线程中执行精修渲染
    def render_task():
        try:
            tasks[task_id]["status"] = "rendering"
            tasks[task_id]["message"] = "正在进行精修渲染..."
            
            scene_file = task.get("scene_file")
            output_dir = get_task_output_dir(task_id)
            
            result = agent.confirm_and_render(
                scene_file=scene_file,
                output_folder=str(output_dir)
            )
            
            if result.get("success"):
                tasks[task_id]["status"] = "completed"
                tasks[task_id]["message"] = "精修渲染完成"
                tasks[task_id]["rendered_image"] = str(result.get("rendered_image", ""))
                tasks[task_id]["needs_confirmation"] = False
            else:
                tasks[task_id]["status"] = "failed"
                tasks[task_id]["message"] = result.get("message", "精修渲染失败")
        except Exception as e:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["message"] = f"精修渲染失败: {str(e)}"
            import traceback
            tasks[task_id]["error"] = traceback.format_exc()
    
    thread = threading.Thread(target=render_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "task_id": task_id,
        "status": "rendering",
        "message": "已确认，正在精修渲染..."
    })


@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """列出所有任务"""
    task_list = []
    for task_id, task in tasks.items():
        task_list.append({
            "task_id": task_id,
            "status": task["status"],
            "message": task.get("message", ""),
            "progress": task.get("progress", 0),
            "created_at": task.get("created_at", ""),
            "user_request": task.get("user_request", "")
        })
    
    # 按创建时间倒序排列
    task_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    return jsonify({"tasks": task_list})


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "agent_initialized": agent is not None,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """提供前端页面"""
    return render_template('index.html')


if __name__ == '__main__':
    print("=" * 60)
    print("Infinigen Web API 服务器")
    print("=" * 60)
    print(f"输出目录: {UPLOAD_FOLDER}")
    print(f"Agent 状态: {'已初始化' if agent else '未初始化'}")
    print("=" * 60)
    print("\n启动服务器...")
    print("API 地址: http://localhost:5000")
    print("\n可用接口:")
    print("  POST /api/generate - 生成场景")
    print("  GET  /api/task/<task_id>/status - 查询任务状态")
    print("  GET  /api/task/<task_id>/image - 获取渲染图片")
    print("  GET  /api/task/<task_id>/download/<file_type> - 下载文件")
    print("  GET  /api/tasks - 列出所有任务")
    print("  GET  /api/health - 健康检查")
    print("\n" + "=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

