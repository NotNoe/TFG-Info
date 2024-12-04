#!/bin/bash

# Archivo: enviar_metrics.sh

# Uso: ./enviar_metrics.sh <ruta_al_metrics.json> <nombre_del_modelo>

# Verificar si se proporcionaron los argumentos necesarios
if [ $# -ne 2 ]; then
    echo "Uso: $0 <ruta_al_metrics.json> <nombre_del_modelo>"
    exit 1
fi

metrics_file="$1"
model_name="$2"

# Verificar que el archivo metrics.json existe
if [ ! -f "$metrics_file" ]; then
    echo "Error: No se encontró el archivo metrics.json en '$metrics_file'"
    exit 1
fi

# Leer el contenido del archivo metrics.json
metrics_content=$(cat "$metrics_file")

# Formatear el contenido del JSON para enviarlo por Telegram
# Usaremos jq para formatear el JSON (asegúrate de que jq está instalado)

if ! command -v jq &> /dev/null; then
    echo "Error: El comando 'jq' no está instalado. Por favor, instálalo para usar este script."
    exit 1
fi

# Formatear el JSON
formatted_metrics=$(jq '.' "$metrics_file")

# Escapar caracteres especiales para MarkdownV2
escaped_metrics=$(echo "$formatted_metrics" | sed -E 's/([_*[\]()~`>#+\-=|{}.!])/\\\1/g')

# Construir el mensaje
message="📊 *Resultados de las métricas para el modelo:* \`${model_name}\`\n\`\`\`\n$escaped_metrics\n\`\`\`"

# Enviar el mensaje por Telegram
./send_telegram.sh "$message"