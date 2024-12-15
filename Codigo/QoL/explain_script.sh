#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

tmp_output=$(mktemp)

cd "$DIR"
cd ..
source /home/mardia35/miniconda3/etc/profile.d/conda.sh
conda activate py38

./QoL/send_telegram.sh "🚀 Iniciando explicaciones."
python QoL/explain.py 2>&1 | tee "$tmp_output"
./QoL/send_telegram.sh "🚀 Explicaciones completadas."
