#!/bin/bash
# 查看模板生成进度的便捷脚本

cd "$(dirname "$0")/.." || exit 1

echo "=========================================="
echo "模板生成进度监控"
echo "=========================================="
echo ""

# 1. 检查进程状态
echo "1. 进程状态:"
PID=$(pgrep -f "generate_template_pool.py")
if [ -n "$PID" ]; then
    echo "   ✓ 进程正在运行 (PID: $PID)"
    ps aux | grep "$PID" | grep -v grep | awk '{print "   内存使用:", $6/1024, "MB | CPU:", $3"%"}'
else
    echo "   ✗ 未找到运行中的进程"
fi
echo ""

# 2. 查看模板池统计
echo "2. 已生成的模板:"
python tools/generate_template_pool.py --list 2>/dev/null | grep -A 20 "模板池统计" || echo "   暂无模板"
echo ""

# 3. 查看日志最后几行
echo "3. 最新日志 (最后10行):"
if [ -f "template_generation.log" ]; then
    tail -n 10 template_generation.log | sed 's/^/   /'
    echo ""
    echo "   日志总行数: $(wc -l < template_generation.log) 行"
    echo "   日志文件大小: $(du -h template_generation.log | cut -f1)"
else
    echo "   ⚠ 日志文件不存在"
fi
echo ""

# 4. 实时查看命令提示
echo "4. 更多查看方式:"
echo "   实时查看日志: tail -f template_generation.log"
echo "   查看完整日志: cat template_generation.log"
echo "   查看模板统计: python tools/generate_template_pool.py --list"
echo ""

