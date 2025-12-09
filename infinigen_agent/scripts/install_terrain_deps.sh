#!/bin/bash
# 安装 Infinigen terrain 依赖的便捷脚本

set -e

echo "="*60
echo "安装 Infinigen Terrain 依赖"
echo "="*60
echo ""

INFINIGEN_ROOT="/home/ubuntu/infinigen"

if [ ! -d "$INFINIGEN_ROOT" ]; then
    echo "错误: Infinigen 根目录不存在: $INFINIGEN_ROOT"
    exit 1
fi

cd "$INFINIGEN_ROOT" || exit 1

# 检查 conda 环境
if ! command -v conda &> /dev/null; then
    echo "错误: conda 未找到，请先安装 conda"
    exit 1
fi

# 激活 conda 环境
echo "[1/2] 激活 infinigen conda 环境..."
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true
conda activate infinigen || {
    echo "错误: 无法激活 infinigen conda 环境"
    exit 1
}

echo "✓ Conda 环境已激活"
echo ""

# 安装 Python 依赖
echo "[2/2] 安装 terrain Python 依赖..."
pip install .[terrain]

echo ""
echo "="*60
echo "✓ Terrain Python 依赖安装完成！"
echo "="*60
echo ""
echo "如果需要编译 C++ 库，请运行:"
echo "  cd $INFINIGEN_ROOT"
echo "  bash scripts/install/compile_terrain.sh"
echo ""
