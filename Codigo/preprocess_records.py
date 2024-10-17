# Ruta del archivo
file_path = './ptbxl/RECORDS'

# Leemos el archivo original, procesamos las líneas y lo sobrescribimos
with open(file_path, 'r') as infile:
    lines = infile.readlines()

with open(file_path, 'w') as outfile:
    for line in lines:
        line = line.strip()  # Eliminamos espacios en blanco al inicio y final de cada línea
        
        # Si la línea termina con _lr, la ignoramos
        if line.endswith('_lr'):
            continue
        
        # Si _lr está en la línea pero no al final, eliminamos desde el inicio hasta _lr
        if '_lr' in line:
            line = line.split('_lr', 1)[1]  # Dividimos y tomamos solo la parte después de _lr
        
        # Escribimos la línea modificada al mismo archivo si no está vacía
        if line:
            outfile.write(line + '\n')

print("El archivo ha sido sobrescrito con las modificaciones.")
