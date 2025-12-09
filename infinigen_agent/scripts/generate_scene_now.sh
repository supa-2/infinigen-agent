#!/bin/bash
# 直接生成一个室内场景

set -e

echo "============================================================"
echo "生成室内场景测试"
echo "============================================================"
echo ""

INFINIGEN_ROOT="/home/ubuntu/infinigen"
OUTPUT_FOLDER="/tmp/test_scene_direct"

cd "$INFINIGEN_ROOT" || exit 1

# 激活 conda 环境
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true
conda activate infinigen || {
    echo "错误: 无法激活 infinigen conda 环境"
    exit 1
}

echo "[1] 检查 landlab 模块..."
if python -c "import landlab" 2>/dev/null; then
    echo "  ✓ landlab 已安装"
else
    echo "  ✗ landlab 未安装，正在安装..."
    pip install .[terrain] || {
        echo "  安装失败，尝试单独安装 landlab..."
        pip install landlab || {
            echo "  ✗ 无法安装 landlab"
            echo "  请手动运行: pip install .[terrain]"
            exit 1
        }
    }
    echo "  ✓ landlab 安装完成"
fi

echo ""
echo "[2] 开始生成场景..."
echo "  输出文件夹: $OUTPUT_FOLDER"
echo "  种子: 0"
echo ""

# 清理旧输出
rm -rf "$OUTPUT_FOLDER"

# 生成场景
python -m infinigen_examples.generate_indoors \
    --output_folder "$OUTPUT_FOLDER" \
    -s 0 \
    -g base disable/no_objects \
    -t coarse

echo ""
echo "[3] 检查生成结果..."

if [ -d "$OUTPUT_FOLDER" ]; then
    echo "  ✓ 输出文件夹已创建"
    
    # 查找 .blend 文件
    blend_files=$(find "$OUTPUT_FOLDER" -name "*.blend" 2>/dev/null | head -5)
    if [ -n "$blend_files" ]; then
        echo "  ✓ 找到场景文件:"
        echo "$blend_files" | while read -r file; do
            echo "    - $file"
        done
    else
        echo "  ⚠ 未找到 .blend 文件"
        echo "  输出目录内容:"
        ls -lah "$OUTPUT_FOLDER" | head -10
    fi
else
    echo "  ✗ 输出文件夹不存在"
fi

echo ""
echo "============================================================"
echo "完成！"
echo "============================================================"
