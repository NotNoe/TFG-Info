#!/bin/bash

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

# Verificar si se proporcionaron los argumentos necesarios
if [ $# -ne 2 ]; then
    echo "Uso: $0 <ruta_al_metrics.json> <nombre_del_modelo>"
    exit 1
fi

metrics_file="$1"
model_name="$2"
escaped_model_name=$(escape_html "$model_name")

# Verificar que el archivo metrics.json existe
if [ ! -f "$metrics_file" ]; then
    echo "Error: No se encontró el archivo metrics.json en '$metrics_file'"
    exit 1
fi

# Usaremos jq para formatear el JSON (asegúrate de que jq está instalado)

if ! command -v jq &> /dev/null; then
    echo "Error: El comando 'jq' no está instalado. Por favor, instálalo para usar este script."
    exit 1
fi

# Leer y formatear el contenido del archivo JSON
METRICS=$(cat "$JSON_FILE" | jq -r 'to_entries | map("\(.key): \(.value)") | join("\n")')

if [ -z "$METRICS" ]; then
    echo "Error: El archivo JSON está vacío o tiene un formato inválido."
    exit 1
fi
ESCAPED_METRICS=$(escape_html "$METRICS")

# Construir el mensaje
message="📊 <b>Métricas para el modelo:</b> <code>${escaped_model_name}</code>\n<pre>${ESCAPED_METRICS}</pre>"

# Enviar el mensaje por Telegram
./send_telegram.sh "$message"