#!/bin/bash
# 安装依赖并生成场景的一体化脚本

set -e

echo "============================================================"
echo "安装依赖并生成室内场景"
echo "============================================================"
echo ""

INFINIGEN_ROOT="/home/ubuntu/infinigen"
OUTPUT_FOLDER="/tmp/test_scene_direct"

cd "$INFINIGEN_ROOT" || exit 1

# 激活 conda 环境
echo "[1/3] 激活 conda 环境..."
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true
conda activate infinigen || {
    echo "✗ 无法激活 infinigen conda 环境"
    exit 1
}
echo "✓ Conda 环境已激活"
echo ""

# 检查并安装 landlab
echo "[2/3] 检查 landlab 依赖..."
if ! python -c "import landlab" 2>/dev/null; then
    echo "⚠ landlab 未安装，正在安装..."
    pip install .[terrain] || {
        echo "✗ 安装失败"
        echo "请手动运行: cd $INFINIGEN_ROOT && pip install .[terrain]"
        exit 1
    }
    echo "✓ landlab 安装完成"
else
    echo "✓ landlab 已安装"
fi
echo ""

# 清理旧输出
echo "[3/3] 生成场景..."
rm -rf "$OUTPUT_FOLDER"

# 生成场景
python -m infinigen_examples.generate_indoors \
    --output_folder "$OUTPUT_FOLDER" \
    -s 0 \
    -g base disable/no_objects \
    -t coarse

echo ""
echo "============================================================"
echo "检查生成结果..."
echo "============================================================"

if [ -d "$OUTPUT_FOLDER" ]; then
    BLEND_FILES=$(find "$OUTPUT_FOLDER" -name "*.blend" 2>/dev/null | wc -l)
    if [ "$BLEND_FILES" -gt 0 ]; then
        echo "✓ 成功生成 $BLEND_FILES 个场景文件:"
        find "$OUTPUT_FOLDER" -name "*.blend" 2>/dev/null | head -5
        echo ""
        echo "场景文件位置: $OUTPUT_FOLDER"
    else
        echo "⚠ 输出目录存在但未找到 .blend 文件"
        echo "目录内容:"
        ls -lah "$OUTPUT_FOLDER" | head -10
    fi
else
    echo "✗ 输出目录不存在，生成可能失败"
fi

echo "============================================================"
