#!/bin/bash
# 启动模板池生成任务的便捷脚本
# 使用 nohup 确保关闭终端后进程继续运行

cd "$(dirname "$0")/.." || exit 1

LOG_FILE="template_generation.log"
PID_FILE="template_generation.pid"

echo "=========================================="
echo "启动模板池生成任务"
echo "=========================================="
echo "日志文件: $LOG_FILE"
echo "PID文件: $PID_FILE"
echo ""

# 检查是否已有任务在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠ 警告: 已有任务在运行 (PID: $OLD_PID)"
        echo "   如果要重新启动，请先运行: ./tools/stop_template_generation.sh"
        exit 1
    else
        echo "清理旧的 PID 文件..."
        rm -f "$PID_FILE"
    fi
fi

# 启动任务
echo "正在启动生成任务..."
nohup python tools/generate_template_pool.py --all > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# 保存 PID
echo $NEW_PID > "$PID_FILE"

echo "✓ 任务已启动 (PID: $NEW_PID)"
echo ""
echo "查看进度:"
echo "  tail -f $LOG_FILE"
echo ""
echo "查看模板池统计:"
echo "  python tools/generate_template_pool.py --list"
echo ""
echo "停止任务:"
echo "  ./tools/stop_template_generation.sh"
echo "  或: kill $NEW_PID"
echo ""

