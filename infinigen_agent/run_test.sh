#!/bin/bash
cd /home/ubuntu/infinigen/infinigen_agent
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate infinigen
python test_langchain_agent.py 2>&1 | tee test_output.log
