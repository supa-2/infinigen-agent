#!/bin/bash
# 官方推荐命令测试脚本

echo "=" | head -c 70; echo
echo "官方推荐命令测试"
echo "=" | head -c 70; echo
echo ""
echo "根据 HelloRoom.md 文档，官方推荐命令："
echo ""
echo "python -m infinigen_examples.generate_indoors \\"
echo "  --seed 0 \\"
echo "  --task coarse \\"
echo "  --output_folder outputs/test_official \\"
echo "  -g fast_solve.gin singleroom.gin \\"
echo "  -p compose_indoors.terrain_enabled=False"
echo ""
echo "预计时间: 8-13 分钟"
echo "=" | head -c 70; echo
echo ""

cd /home/ubuntu/infinigen
TIMESTAMP=$(date +%s)
OUTPUT_FOLDER="outputs/test_official_${TIMESTAMP}"

echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "输出文件夹: ${OUTPUT_FOLDER}"
echo ""

python -m infinigen_examples.generate_indoors \
  --seed 0 \
  --task coarse \
  --output_folder "${OUTPUT_FOLDER}" \
  -g fast_solve.gin singleroom.gin \
  -p compose_indoors.terrain_enabled=False

EXIT_CODE=$?

echo ""
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "退出代码: ${EXIT_CODE}"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 测试成功！"
    echo "场景文件: ${OUTPUT_FOLDER}/scene.blend"
else
    echo "❌ 测试失败"
fi
