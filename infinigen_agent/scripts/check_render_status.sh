#!/bin/bash
# 检查渲染状态

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
INFINIGEN_ROOT="/home/ubuntu/infinigen"
OUTPUT_FOLDER="$INFINIGEN_ROOT/outputs/hello_room/coarse/frames_render"
LOG_FILE="/tmp/render_log.txt"

echo "=========================================="
echo "检查渲染状态"
echo "=========================================="
echo ""

# 1. 检查进程
echo -e "${BLUE}1. 渲染进程:${NC}"
render_processes=$(ps aux | grep "generate_indoors.*render" | grep -v grep)
if [ -n "$render_processes" ]; then
    echo -e "${GREEN}✓ 发现运行中的渲染进程:${NC}"
    echo "$render_processes" | while read -r line; do
        pid=$(echo "$line" | awk '{print $2}')
        cpu=$(echo "$line" | awk '{print $3}')
        mem=$(echo "$line" | awk '{print $4}')
        cmd=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
        echo "  PID: $pid | CPU: $cpu% | MEM: $mem%"
        echo "  命令: $cmd"
    done
else
    echo -e "${YELLOW}  无运行中的渲染进程${NC}"
fi

echo ""

# 2. 检查日志文件
echo -e "${BLUE}2. 日志文件:${NC}"
if [ -f "$LOG_FILE" ]; then
    log_size=$(du -h "$LOG_FILE" | cut -f1)
    log_lines=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ 日志文件存在${NC}"
    echo "  路径: $LOG_FILE"
    echo "  大小: $log_size"
    echo "  行数: $log_lines"
    echo ""
    echo "  最后20行:"
    echo "  ----------------------------------------"
    tail -20 "$LOG_FILE" | sed 's/^/  /'
    echo "  ----------------------------------------"
    
    # 检查错误
    error_count=$(grep -i "error\|failed\|exception" "$LOG_FILE" | wc -l)
    if [ "$error_count" -gt 0 ]; then
        echo ""
        echo -e "${RED}⚠ 发现 $error_count 个可能的错误${NC}"
        echo "  最近的错误:"
        grep -i "error\|failed\|exception" "$LOG_FILE" | tail -3 | sed 's/^/  /'
    fi
else
    echo -e "${YELLOW}  日志文件不存在${NC}"
fi

echo ""

# 3. 检查输出文件
echo -e "${BLUE}3. 输出文件:${NC}"
if [ -d "$OUTPUT_FOLDER" ]; then
    echo -e "${GREEN}✓ 输出文件夹存在${NC}"
    echo "  路径: $OUTPUT_FOLDER"
    
    # 统计文件
    png_count=$(find "$OUTPUT_FOLDER" -name "*.png" 2>/dev/null | wc -l)
    json_count=$(find "$OUTPUT_FOLDER" -name "*.json" 2>/dev/null | wc -l)
    total_size=$(du -sh "$OUTPUT_FOLDER" 2>/dev/null | cut -f1)
    
    echo "  PNG 文件: $png_count"
    echo "  JSON 文件: $json_count"
    echo "  总大小: $total_size"
    
    if [ "$png_count" -gt 0 ]; then
        echo ""
        echo "  示例 PNG 文件（前5个）:"
        find "$OUTPUT_FOLDER" -name "*.png" 2>/dev/null | head -5 | while read -r file; do
            size=$(du -h "$file" | cut -f1)
            mtime=$(stat -c %y "$file" 2>/dev/null | cut -d'.' -f1)
            echo "    - $(basename "$file") ($size, 修改时间: $mtime)"
        done
        
        # 检查最新文件
        latest_file=$(find "$OUTPUT_FOLDER" -name "*.png" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        if [ -n "$latest_file" ]; then
            latest_time=$(stat -c %y "$latest_file" 2>/dev/null | cut -d'.' -f1)
            echo ""
            echo "  最新文件: $(basename "$latest_file")"
            echo "  修改时间: $latest_time"
        fi
    else
        echo -e "${YELLOW}  ⚠ 未找到 PNG 文件${NC}"
        echo "  文件夹内容:"
        ls -lah "$OUTPUT_FOLDER" | head -10 | sed 's/^/    /' || true
    fi
else
    echo -e "${RED}✗ 输出文件夹不存在${NC}"
fi

echo ""
echo "=========================================="
echo "状态检查完成"
echo "=========================================="

