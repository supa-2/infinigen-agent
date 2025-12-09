#!/bin/bash
# 将单帧图片转换为视频（静态画面）

set -e

IMAGE_PATH="/home/ubuntu/infinigen/outputs/hello_room/coarse/frames/Image/camera_0/Image_0_0_0001_0.png"
VIDEO_OUTPUT="/home/ubuntu/infinigen/outputs/hello_room/coarse/video_static.mp4"
DURATION=${1:-5}   # 默认5秒
FPS=${2:-24}       # 默认24fps

echo "=========================================="
echo "生成静态视频"
echo "=========================================="
echo "图片: $IMAGE_PATH"
echo "输出: $VIDEO_OUTPUT"
echo "时长: ${DURATION}秒"
echo "帧率: ${FPS} fps"
echo ""

# 检查图片是否存在
if [ ! -f "$IMAGE_PATH" ]; then
    echo "✗ 图片文件不存在: $IMAGE_PATH"
    exit 1
fi

# 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "✗ ffmpeg 未安装，请先安装: sudo apt install ffmpeg"
    exit 1
fi

# 计算需要的帧数
TOTAL_FRAMES=$((DURATION * FPS))

echo "正在生成视频（${TOTAL_FRAMES}帧）..."

# 使用 ffmpeg 将单帧图片转换为视频
ffmpeg -y \
    -loop 1 \
    -i "$IMAGE_PATH" \
    -t ${DURATION} \
    -r ${FPS} \
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
    echo "时长: ${DURATION}秒"
else
    echo "✗ 视频生成失败"
    exit 1
fi
