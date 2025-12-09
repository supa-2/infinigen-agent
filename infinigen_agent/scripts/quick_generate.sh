#!/bin/bash
set -e

cd /home/ubuntu/infinigen
source ~/miniconda3/etc/profile.d/conda.sh
conda activate infinigen

echo "检查 landlab 依赖..."
if ! python -c "import landlab" 2>/dev/null; then
    echo "⚠ landlab 未安装，正在安装 terrain 依赖..."
    pip install .[terrain] || {
        echo "✗ 安装失败，请手动运行: pip install .[terrain]"
        exit 1
    }
    echo "✓ 依赖安装完成"
else
    echo "✓ landlab 已安装"
fi

echo ""
echo "开始生成场景..."
rm -rf /tmp/test_scene_direct

python -m infinigen_examples.generate_indoors \
    --output_folder /tmp/test_scene_direct \
    -s 0 \
    -g base disable/no_objects \
    -t coarse

echo ""
echo "检查结果..."
find /tmp/test_scene_direct -name "*.blend" 2>/dev/null | head -5
