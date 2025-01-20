import os
import shutil
# Ruta del archivo


# Lista de archivos a eliminar
files_to_delete = ["LICENSE.txt", "SHA256SUMS.txt", "example_physionet.py", "ptbxl_v102_changelog.txt", "ptbxl_v103_changelog.txt"]
for file in files_to_delete:
    file_path = os.path.join("ptbxl", file)
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"El archivo {file} ha sido eliminado.")
    else:
        print(f"El archivo {file} no se encontró en la carpeta ptbxl.")
if os.path.isdir('ptbxl/records100'):
    shutil.rmtree('ptbxl/records100')  # Eliminamos la carpeta records100
    print("La carpeta records100 ha sido eliminada.")
else:
    print("La carpeta records100 no se encontró en la carpeta ptbxl.")
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
