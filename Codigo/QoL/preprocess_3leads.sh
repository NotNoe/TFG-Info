#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
tmp_output=$(mktemp)

cd "$DIR"
cd ..
source ~/miniconda3/etc/profile.d/conda.sh
conda activate py38
export TF_CPP_MIN_LOG_LEVEL=3
./QoL/send_telegram.sh "🚀 Iniciando preprocesamiento de registros para 3 leads."
python scripts/preprocess_data_3leads.py 2>&1 | tee "$tmp_output"
exit_status=${PIPESTATUS[0]}
if [ $exit_status -ne 0 ]; then
    ./QoL/send_telegram.sh "❌ Error en preprocesamiento de registros para 3 leads."
    exit 1
fi
./QoL/send_telegram.sh "✅ Preprocesamiento de registros para 3 leads completado."
