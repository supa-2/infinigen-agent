#!/bin/bash
# 从场景生成视频 - 渲染多帧并合成视频

set -e

cd /home/ubuntu/infinigen
source ~/miniconda3/etc/profile.d/conda.sh
conda activate infinigen

SCENE_PATH="outputs/hello_room/coarse/scene.blend"
FRAMES_DIR="outputs/hello_room/coarse/video_frames"
VIDEO_OUTPUT="outputs/hello_room/coarse/video_output.mp4"
FRAMES=${1:-30}   # 默认30帧
FPS=${2:-24}      # 默认24fps

echo "=========================================="
echo "开始生成视频"
echo "=========================================="
echo "场景: $SCENE_PATH"
echo "帧数: $FRAMES"
echo "帧率: $FPS fps"
echo "输出: $VIDEO_OUTPUT"
echo ""

# 创建输出文件夹
mkdir -p "$FRAMES_DIR"

echo "正在渲染 $FRAMES 帧..."
echo "提示: 这可能需要较长时间（每帧约12分钟）"
echo ""

# 渲染多帧
for i in $(seq 1 $FRAMES); do
    frame_num=$(printf "%04d" $i)
    echo "[$i/$FRAMES] 正在渲染第 $i 帧..."
    
    # 使用 Infinigen 渲染单帧
    python -m infinigen_examples.generate_indoors \
        --seed 0 \
        --task render \
        --input_folder outputs/hello_room/coarse \
        --output_folder "$FRAMES_DIR/frame_$frame_num" \
        > /tmp/render_frame_${i}.log 2>&1
    
    # 复制主图片到视频帧文件夹
    if [ -f "$FRAMES_DIR/frame_$frame_num/frames/Image/camera_0/Image_0_0_0001_0.png" ]; then
        cp "$FRAMES_DIR/frame_$frame_num/frames/Image/camera_0/Image_0_0_0001_0.png" \
           "$FRAMES_DIR/frame_${frame_num}.png"
        echo "  ✓ 第 $i 帧完成"
    else
        echo "  ✗ 第 $i 帧失败"
    fi
done

echo ""
echo "正在使用 ffmpeg 合成视频..."

# 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "✗ ffmpeg 未安装，请先安装: sudo apt install ffmpeg"
    exit 1
fi

# 使用 ffmpeg 合成视频
ffmpeg -y \
    -r $FPS \
    -pattern_type glob \
    -i "$FRAMES_DIR/frame_*.png" \
    -pix_fmt yuv420p \
    -vcodec libx264 \
    "$VIDEO_OUTPUT"

if [ -f "$VIDEO_OUTPUT" ]; then
    size_mb=$(du -h "$VIDEO_OUTPUT" | cut -f1)
    echo ""
    echo "=========================================="
    echo "✓ 视频生成完成！"
    echo "=========================================="
    echo "视频文件: $VIDEO_OUTPUT"
    echo "文件大小: $size_mb"
else
    echo "✗ 视频生成失败"
    exit 1
fi
