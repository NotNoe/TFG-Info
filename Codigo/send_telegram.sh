#!/bin/bash
#Variables de entorno
TOKEN="7901058857:AAF0EMIMNGfIyI0KWgwG17qE2D9IDG_T8pA"
CHAT_ID="791760956"

# Comprobar si se proporcionó un mensaje
if [ $# -eq 0 ]; then
    echo "Uso: $0 \"mensaje a enviar\""
    exit 1
fi

# Concatenar todos los argumentos en un solo mensaje
MENSAJE="$*"

# Enviar el mensaje al bot de Telegram
curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
     -d chat_id="$CHAT_ID" \
     -d text="$MENSAJE" \
     -d parse_mode="MarkdownV2" \
     > /dev/null 2>&1