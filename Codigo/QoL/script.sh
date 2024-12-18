#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

tracings=("stft" "cwt_morlet" "cwt_ricker")
output_dir="./final_models"

tmp_output=$(mktemp)

cd "$DIR"
cd ..
source ~/miniconda3/etc/profile.d/conda.sh
conda activate py38

./QoL/send_telegram.sh "🚀 Iniciando script."

#Descargamos ptbxl
#./QoL/send_telegram.sh "🚀 Descargando ptbxl."
#wget -r -N -c -np -i QoL/index.txt -P ptbxl | tee "$tmp_output"
#./QoL/send_telegram.sh "🚀 Descarga de ptbxl completada."
#mv ptbxl/physionet.org/files/ptb-xl/1.0.3/* ptbxl/
#rm -r ptbxl/physionet.org
#rm QoL/index.html


# Primero corremos preprocess_records.py
./QoL/send_telegram.sh "🚀 Iniciando preprocesamiento de registros."
python scripts/preprocess_records.py 2>&1 | tee "$tmp_output"
./QoL/send_telegram.sh "🚀 Preprocesamiento de registros completado."
./QoL/send_telegram.sh "🚀 Iniciando preprocesamiento de datos."
python scripts/preprocess_data.py 2>&1 | tee "$tmp_output"
./QoL/send_telegram.sh "🚀 Preprocesamiento de datos completado."

#Hacemos las transformaciones
./QoL/send_telegram.sh "🚀 Iniciando transformaciones."
python scripts/transform_data_stft.py 2>&1 | tee "$tmp_output"
./QoL/send_telegram.sh "🚀 Stft completada."
python scripts/transform_data_cwt_morlet.py 2>&1 | tee "$tmp_output"
./QoL/send_telegram.sh "🚀 Cwt morlet completada."
python scripts/transform_data_cwt_ricker.py 2>&1 | tee "$tmp_output"
./QoL/send_telegram.sh "🚀 Cwt ricker completada."

#Hacemos aux para sacar las explicaciones que queriamos
./QoL/send_telegram.sh "🚀 Iniciando explicaciones."
python QoL/explain.py 2>&1 | tee "$tmp_output"
./QoL/send_telegram.sh "🚀 Explicaciones completadas."

./QoL/send_telegram.sh "🚀 Iniciando entrenamiento de modelos transformados."

# Ruta al script de Python que entrena el modelo
python_script="ribeiro/train.py"

# Verificar si el script de Python existe
if [ ! -f "$python_script" ]; then
    echo -e "Error: No se encontró el script de Python '$python_script'."
    exit 1
fi



# Función para escapar caracteres especiales en HTML
escape_html() {
    echo -e "$1" | awk '
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
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando entrenamiento para tracing: ${tracing_name}"
    ./QoL/send_telegram.sh "🚀 Iniciando entrenamiento para tracing: <code>${escaped_tracing_name}</code>"

    # Ejecutar el script de Python y capturar el código de salida
    python "$python_script" "$tracing_name" --output_file "$output_path" 2>&1 | tee "$tmp_output"
    exit_status=${PIPESTATUS[0]}

    # Verificar si el entrenamiento fue exitoso
    if [ $exit_status -eq 0 ]; then
        echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] Entrenamiento completado exitosamente para tracing: ${tracing_name}"
        message="✅ <b>Entrenamiento completado exitosamente para tracing:</b> <code>${escaped_tracing_name}</code>"
        # Log: Iniciando pruebas del modelo
        echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando pruebas para el modelo: ${model_name}"
        # Ejecutar el script test_model.py
        python scripts/test_model.py "$model_name" "$tracing_name" 2>&1 | tee "$tmp_output"
        test_exit_status=${PIPESTATUS[0]}

        if [ $test_exit_status -eq 0 ]; then
            echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] Pruebas completadas para el modelo: ${model_name}"

            message+="%0A🔍 <b>Pruebas completadas para el modelo:</b> <code>${escaped_model_name}</code>"

            # Enviar mensaje de éxito
            ./QoL/send_telegram.sh "$message"

            # Ruta al archivo metrics.json
            metrics_file="./test/${model_name}/metrics.json"

            # Verificar que el archivo metrics.json existe
            if [ -f "$metrics_file" ]; then
                echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] Enviando métricas para el modelo: ${model_name}"
                # Llamar al script que formatea y envía el JSON
                ./QoL/send_metrics.sh "$metrics_file" "$model_name"
            else
                echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] No se encontró metrics.json para el modelo: ${model_name}"

                # Enviar advertencia si no se encuentra metrics.json
                ./QoL/send_telegram.sh "⚠️ No se encontró el archivo <code>metrics.json</code> para el modelo <code>${escaped_model_name}</code>"
            fi
        else
            # Hubo un error al ejecutar test_model.py
            echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] Error al ejecutar test_model.py para el modelo: ${model_name}"
            cat "$tmp_output"
            test_output_truncated=$(cat "$tmp_output" | head -c 3500)
            message+="%0A❌ <b>Error al ejecutar test_model.py:</b>%0A<pre>${test_output_truncated}</pre>"
            ./QoL/send_telegram.sh "$message"
        fi

    else
        # Hubo un error durante el entrenamiento
        echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] Error en el entrenamiento para tracing: ${tracing_name}"
        message="❌ <b>Error en el entrenamiento para tracing:</b> <code>${escaped_tracing_name}</code>"
        # Enviar mensaje con el error
        ./QoL/send_telegram.sh "$message"
    fi
done
# Log: Finalización de todas las tareas
echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] Todos los entrenamientos y pruebas han finalizado."

# Enviar mensaje indicando que todas las tareas han finalizado
"$DIR/send_telegram.sh" "🏁 <b>Todos los entrenamientos y pruebas han finalizado.</b>"

