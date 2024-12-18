#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate py38
export TF_CPP_MIN_LOG_LEVEL=3

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

python aux.py
./QoL/send_telegram.sh "Explicaciones terminadas en local"