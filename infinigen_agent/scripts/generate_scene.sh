#!/bin/bash
# Infinigen 场景生成脚本
# 用于 Agent 直接调用 Infinigen 原生命令

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFINIGEN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 默认参数
OUTPUT_FOLDER=""
SEED=""
TASK=("coarse")  # 支持多个任务
GIN_CONFIGS=("base" "disable/no_objects")
TIMEOUT=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-folder)
            OUTPUT_FOLDER="$2"
            shift 2
            ;;
        -s|--seed)
            SEED="$2"
            shift 2
            ;;
        -t|--task)
            # 支持多个任务，收集所有任务参数
            TASK=()
            shift
            while [[ $# -gt 0 ]] && [[ ! "$1" =~ ^- ]]; do
                TASK+=("$1")
                shift
            done
            ;;
        -g|--gin-config)
            GIN_CONFIGS+=("$2")
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查必需参数
if [[ -z "$OUTPUT_FOLDER" ]]; then
    echo "错误: 必须指定 --output-folder"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_FOLDER"

# 构建命令
CMD="python -m infinigen_examples.generate_indoors"
CMD="$CMD --output_folder \"$OUTPUT_FOLDER\""
CMD="$CMD -s \"$SEED\""
CMD="$CMD -t"
# 添加所有任务（支持多个任务，如 coarse render）
for task in "${TASK[@]}"; do
    CMD="$CMD \"$task\""
done

# 添加 gin 配置
for config in "${GIN_CONFIGS[@]}"; do
    CMD="$CMD -g \"$config\""
done

# 切换到 Infinigen 根目录
cd "$INFINIGEN_ROOT"

echo "============================================================"
echo "Infinigen 场景生成"
echo "============================================================"
echo "输出文件夹: $OUTPUT_FOLDER"
echo "种子: $SEED"
echo "任务: ${TASK[*]}"
if [[ ${#TASK[@]} -gt 1 ]]; then
    echo "⚠ 将一次完成多个任务"
fi
echo "Gin 配置: ${GIN_CONFIGS[*]}"
echo "命令: $CMD"
echo "============================================================"

# 执行命令
if [[ -n "$TIMEOUT" ]]; then
    timeout "$TIMEOUT" bash -c "$CMD"
else
    eval "$CMD"
fi

echo "============================================================"
echo "场景生成完成"
echo "============================================================"

