#!/bin/bash
# 简单的视频渲染脚本

cd /home/ubuntu/infinigen
source ~/miniconda3/etc/profile.d/conda.sh
conda activate infinigen

SCENE_PATH="outputs/hello_room/coarse/scene.blend"
OUTPUT_FOLDER="outputs/hello_room/coarse/video_output"
FRAMES=${1:-10}  # 默认10帧，可以通过参数指定
FPS=${2:-24}     # 默认24fps

echo "=========================================="
echo "开始渲染视频"
echo "=========================================="
echo "场景: $SCENE_PATH"
echo "输出: $OUTPUT_FOLDER"
echo "帧数: $FRAMES"
echo "帧率: $FPS fps"
echo ""

# 使用 run_agent.py 渲染视频
python infinigen_agent/run_agent.py \
    "渲染视频" \
    "$SCENE_PATH" \
    --render-video \
    --video-frames $FRAMES \
    --video-fps $FPS \
    --resolution 1280 720

echo ""
echo "=========================================="
echo "视频渲染完成"
echo "=========================================="
