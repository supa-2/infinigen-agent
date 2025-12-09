#!/bin/bash
# 修复 marching_cubes 模块 - 只编译 Cython 扩展，不重新安装包

set -e

cd /home/ubuntu/infinigen
source ~/miniconda3/etc/profile.d/conda.sh
conda activate infinigen

echo "============================================================"
echo "编译 marching_cubes Cython 扩展模块"
echo "============================================================"
echo ""
echo "注意：这只会编译扩展模块（.pyx → .so），不会重新安装 Infinigen"
echo ""

# 环境变量说明：
# - INFINIGEN_MINIMAL_INSTALL=False: 必需！如果为 True，setup.py 不会编译任何 Cython 扩展
# - INFINIGEN_INSTALL_TERRAIN=True: 推荐！确保编译 terrain 相关扩展（默认就是 True，但显式设置更安全）
export INFINIGEN_INSTALL_TERRAIN=True
export INFINIGEN_MINIMAL_INSTALL=False

echo "开始编译..."
python setup.py build_ext --inplace

echo ""
echo "============================================================"
echo "验证编译结果..."
echo "============================================================"

python -c "from infinigen.terrain import marching_cubes; print('✓ marching_cubes 导入成功'); print('LutProvider 存在:', hasattr(marching_cubes, 'LutProvider') or 'LutProvider' in str(dir(marching_cubes)))" 2>&1

echo ""
echo "============================================================"
