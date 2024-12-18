import json
import sys

def format_json(data, indent=0):
    """Formatea un objeto JSON con tabulación y saltos de línea."""
    result = []
    spacer = "    "  # 4 espacios por nivel de indentación
    prefix = spacer * indent

    if isinstance(data, dict):
        for key, value in data.items():
            result.append(f"{prefix}{key}:")
            result.append(format_json(value, indent + 1))
    elif isinstance(data, list):
        for item in data:
            result.append(f"{prefix}- {format_json(item, indent + 1).strip()}")
    else:
        # Convertir valores simples a cadena
        result.append(f"{prefix}{data}")

    return "\n".join(result)

def main():
    if len(sys.argv) < 2:
        print("Uso: python format_json.py <ruta_al_archivo_json>")
        sys.exit(1)

    json_file = sys.argv[1]
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
        print(format_json(data))
    except Exception as e:
        print(f"Error al procesar el archivo JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
