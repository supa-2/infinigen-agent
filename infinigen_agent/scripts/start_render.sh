#!/bin/bash
cd /home/ubuntu/infinigen
source ~/miniconda3/etc/profile.d/conda.sh
conda activate infinigen
python -m infinigen_examples.generate_indoors \
    --seed 0 \
    --task render \
    --input_folder outputs/hello_room/coarse \
    --output_folder outputs/hello_room/coarse/frames_render \
    > /tmp/render_output.log 2>&1 &
echo $! > /tmp/render_pid.txt
echo "渲染已启动，PID: $(cat /tmp/render_pid.txt)"
echo "日志文件: /tmp/render_output.log"
