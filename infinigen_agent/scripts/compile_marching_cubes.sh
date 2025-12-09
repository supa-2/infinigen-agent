#!/bin/bash
# 编译 marching_cubes Cython 模块

set -e

echo "============================================================"
echo "编译 marching_cubes Cython 模块"
echo "============================================================"
echo ""

INFINIGEN_ROOT="/home/ubuntu/infinigen"

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

# 检查 Cython
echo "[2/3] 检查依赖..."
if ! python -c "import Cython" 2>/dev/null; then
    echo "⚠ Cython 未安装，正在安装..."
    pip install Cython || {
        echo "✗ Cython 安装失败"
        exit 1
    }
    echo "✓ Cython 已安装"
else
    echo "✓ Cython 已安装"
fi

if ! python -c "import numpy" 2>/dev/null; then
    echo "✗ numpy 未安装"
    exit 1
fi
echo "✓ numpy 已安装"
echo ""

# 编译 marching_cubes
echo "[3/3] 编译 marching_cubes 模块..."
export INFINIGEN_INSTALL_TERRAIN=True
export INFINIGEN_MINIMAL_INSTALL=False

python setup.py build_ext --inplace || {
    echo "✗ 编译失败"
    exit 1
}

echo ""
echo "============================================================"
echo "检查编译结果..."
echo "============================================================"

if [ -f "$INFINIGEN_ROOT/infinigen/terrain/marching_cubes/_marching_cubes_lewiner_cy.so" ] || \
   [ -f "$INFINIGEN_ROOT/infinigen/terrain/marching_cubes/_marching_cubes_lewiner_cy*.so" ]; then
    echo "✓ marching_cubes 模块编译成功！"
    find "$INFINIGEN_ROOT/infinigen/terrain/marching_cubes" -name "*.so" 2>/dev/null
else
    echo "⚠ 未找到编译的 .so 文件，但可能已编译到其他位置"
    echo "检查 Python 导入..."
    python -c "from infinigen.terrain import marching_cubes; print('✓ 模块可以导入'); print('属性:', [x for x in dir(marching_cubes) if 'Lut' in x])" 2>&1 || {
        echo "✗ 模块无法导入"
        exit 1
    }
fi

echo "============================================================"
