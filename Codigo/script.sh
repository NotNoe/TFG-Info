#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

training_data=("stft" "cwt_morlet" "cwt_ricker")
output_dir="./final_models"

cd "$DIR"
source /home/noebg2009/miniconda3/etc/profile.d/conda.sh
conda activate py38

for tracing_name in "${tracings[@]}"; do
    # Construir el path de salida para el modelo
    model_name="${tracing_name}_model"
    output_path="${output_dir}/${model_name}.hdf5"

    # Enviar mensaje indicando que se inicia el entrenamiento
    echo "🚀 Iniciando entrenamiento para tracing: ${tracing_name}"
    ./send_telegram.sh "🚀 Iniciando entrenamiento para tracing: ${tracing_name}"

    # Ejecutar el script de Python y capturar el código de salida
    output=$(python "$python_script" "$tracing_name" "$output_path" 2>&1)
    exit_status=$?

    # Verificar si el entrenamiento fue exitoso
    if [ $exit_status -eq 0 ]; then
	echo "✅ Entrenamiento completado exitosamente para tracing: ${tracing_name}"
        message="✅ Entrenamiento completado exitosamente para tracing: ${tracing_name}"



    else
	# Truncar la salida de error si es demasiado larga
        truncated_output=$(echo "$output" | head -c 3500)
        # Escapar caracteres especiales para MarkdownV2
        escaped_output=$(echo "$truncated_output" | sed -E 's/([_*[\]()~`>#+\-=|{}.!])/\\\1/g')
	echo "❌ *Error en el entrenamiento para tracing:* \`${tracing_name}"
        message="❌ *Error en el entrenamiento para tracing:* \`${tracing_name}\`\n*Salida de error:*\n\`\`\`\n$escaped_output\n\`\`\`"
    fi

    # Enviar mensaje con el resultado del entrenamiento
    ./send_telegram.sh "$message"
done

# Enviar mensaje indicando que todas las tareas han finalizado
echo "🏁 *Todos los entrenamientos han finalizado.*"
./send_telegram.sh "🏁 *Todos los entrenamientos han finalizado.*"
