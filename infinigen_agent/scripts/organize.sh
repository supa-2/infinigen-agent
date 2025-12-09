#!/bin/bash
# 整理项目文件结构

cd "$(dirname "$0")/.."

# 创建目录
mkdir -p docs tests scripts tools

# 移动文档文件
for f in CHANGELOG.md COLOR_LOGIC.md EXPLAIN_COMPILE.md FURNITURE_LOCATIONS.md \
         PROJECT_STRUCTURE.md QUICK_START.md RENDERING.md TEST_RESULTS.md \
         TESTING.md TROUBLESHOOTING.md USAGE.md video_time_estimate.md; do
    [ -f "$f" ] && mv "$f" docs/ && echo "Moved $f to docs/"
done

# 移动测试文件
for f in test_*.py; do
    [ -f "$f" ] && mv "$f" tests/ && echo "Moved $f to tests/"
done

# 移动脚本文件（除了当前脚本）
for f in *.sh; do
    [ -f "$f" ] && [ "$f" != "organize.sh" ] && mv "$f" scripts/ && echo "Moved $f to scripts/"
done

# 移动工具文件
for f in quick_test*.py quick_render_test.py generate_scene_direct.py \
         monitor_render.py render_test.py render_video.py create_video.py; do
    [ -f "$f" ] && mv "$f" tools/ && echo "Moved $f to tools/"
done

echo "文件整理完成！"
