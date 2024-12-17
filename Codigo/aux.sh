#!/bin/bash
source /home/noe/miniconda3/etc/profile.d/conda.sh
conda activate py38

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

python aux.py
./QoL/send_telegram.sh "Explicaciones terminadas en local"