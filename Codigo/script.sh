#!/bin/bash
exec 3>&1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

tracings=("stft" "cwt_morlet" "cwt_ricker")
output_dir="./final_models"

# Ruta al script de Python que entrena el modelo
python_script="ribeiro/train.py"

# Verificar si el script de Python existe
if [ ! -f "$python_script" ]; then
    echo "Error: No se encontró el script de Python '$python_script'."
    exit 1
fi

cd "$DIR"
source /home/noebg2009/miniconda3/etc/profile.d/conda.sh
conda activate py38

# Función para escapar caracteres especiales en HTML
escape_html() {
    echo "$1" | awk '
    {
        while (match($0, /<[^>]+>/)) {
            # Capturar texto antes, la etiqueta HTML, y el texto después
            before = substr($0, 1, RSTART - 1)
            tag = substr($0, RSTART, RLENGTH)
            $0 = substr($0, RSTART + RLENGTH)

            # Escapar el texto antes de la etiqueta
            gsub("&", "&amp;", before)
            gsub("<", "&lt;", before)
            gsub(">", "&gt;", before)

            # Reconstruir la línea
            printf "%s%s", before, tag
        }

        # Procesar el resto del texto (sin etiquetas)
        gsub("&", "&amp;")
        gsub("<", "&lt;")
        gsub(">", "&gt;")
        printf "%s\n", $0
    }'
}

for tracing_name in "${tracings[@]}"; do
    # Construir el path de salida para el modelo
    model_name="${tracing_name}_model"
    output_path="${output_dir}/${model_name}.hdf5"
    escaped_model_name=$(escape_html "$model_name")
    escaped_tracing_name=$(escape_html "$tracing_name")


    # Enviar mensaje indicando que se inicia el entrenamiento
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando entrenamiento para tracing: ${tracing_name}"
    ./send_telegram.sh "🚀 Iniciando entrenamiento para tracing: <code>${escaped_tracing_name}</code>"

    # Ejecutar el script de Python y capturar el código de salida
    output=$(python "$python_script" "$tracing_name" --output_file "$output_path" 2>&1 | tee /dev/fd/3)
    exit_status=$?

    # Verificar si el entrenamiento fue exitoso
    if [ $exit_status -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Entrenamiento completado exitosamente para tracing: ${tracing_name}"
        message="✅ <b>Entrenamiento completado exitosamente para tracing:</b> <code>${escaped_tracing_name}</code>"
        # Log: Iniciando pruebas del modelo
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando pruebas para el modelo: ${model_name}"
        # Ejecutar el script test_model.py
        test_output=$(python scripts/test_model.py "$model_name" "$tracing_name" 2>&1 | tee /dev/fd/3)
        test_exit_status=$?

        if [ $test_exit_status -eq 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pruebas completadas para el modelo: ${model_name}"

            message+="<br>🔍 <b>Pruebas completadas para el modelo:</b> <code>${escaped_model_name}</code>"

            # Enviar mensaje de éxito
            ./send_telegram.sh "$message"

            # Ruta al archivo metrics.json
            metrics_file="./test/${model_name}/metrics.json"

            # Verificar que el archivo metrics.json existe
            if [ -f "$metrics_file" ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] Enviando métricas para el modelo: ${model_name}"
                # Llamar al script que formatea y envía el JSON
                ./send_metrics.sh "$metrics_file" "$model_name"
            else
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] No se encontró metrics.json para el modelo: ${model_name}"

                # Enviar advertencia si no se encuentra metrics.json
                ./send_telegram.sh "⚠️ No se encontró el archivo <code>metrics.json</code> para el modelo <code>${escaped_model_name}</code>"
            fi
        else
            # Hubo un error al ejecutar test_model.py
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error al ejecutar test_model.py para el modelo: ${model_name}"

            test_output_truncated=$(echo "$test_output" | head -c 3500)
            message+="<br>❌ <b>Error al ejecutar test_model.py:</b><br><pre>${test_output_truncated}</pre>"
            ./send_telegram.sh "$message"
        fi

    else
        # Hubo un error durante el entrenamiento
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error en el entrenamiento para tracing: ${tracing_name}"

        output_truncated=$(echo "$output" | head -c 3500)
        escaped_output=$(escape_html "$output_truncated")
        message="❌ <b>Error en el entrenamiento para tracing:</b> <code>${escaped_tracing_name}</code><br><b>Salida de error:</b>\n<pre>${escaped_output}</pre>"
        # Enviar mensaje con el error
        ./send_telegram.sh "$message"
    fi
done
# Log: Finalización de todas las tareas
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Todos los entrenamientos y pruebas han finalizado."

# Enviar mensaje indicando que todas las tareas han finalizado
"$DIR/send_telegram.sh" "🏁 <b>Todos los entrenamientos y pruebas han finalizado.</b>"

