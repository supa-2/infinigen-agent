#!/bin/bash
# 停止模板池生成任务的脚本

cd "$(dirname "$0")/.." || exit 1

PID_FILE="template_generation.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "未找到 PID 文件，尝试查找进程..."
    PID=$(pgrep -f "generate_template_pool.py")
    if [ -z "$PID" ]; then
        echo "✗ 未找到运行中的生成任务"
        exit 1
    fi
else
    PID=$(cat "$PID_FILE")
fi

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "✗ 进程 (PID: $PID) 不在运行"
    rm -f "$PID_FILE"
    exit 1
fi

echo "正在停止任务 (PID: $PID)..."
kill "$PID"

# 等待进程结束
sleep 2

if ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠ 进程仍在运行，强制终止..."
    kill -9 "$PID"
fi

rm -f "$PID_FILE"
echo "✓ 任务已停止"

