import json
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import h5py
import pandas as pd
import sys

#Nombres de las etiquetas
label_names = ["CD", "HYP", "MI", "NORM", "STTC"]

# --- Carga de datos ---
# Cargamos los datos de pruebas
test_x = h5py.File('./data/test.hdf5', 'r')["tracings"]

# Cargamos las etiquetas desde el CSV
df = pd.read_csv('./data/test_db.csv')
test_y = df.drop(columns=['ecg_id']).to_numpy()

# --- Ejecución del modelo ---

# Obtenemos las predicciones mediante el script original de Ribeiro
os.system("python ./ribeiro/predict.py data/test.hdf5 final_models/original_model.hdf5 --output_file ./tmp.npy --dataset_name tracings")

# Las cargamos
predictions = np.load("./tmp.npy")

# Y las convertimos a booleanos
predictions = predictions > 0.5

# --- Comparación de resultados ---

# Comprobamos que la forma de las predicciones sea correcta
if predictions.shape[0] != test_y.shape[0]:
    print("The number of test samples and predictions do not match")
    sys.exit(1)
if predictions.shape[1] != test_y.shape[1] or predictions.shape[1] != 5:
    print("The number of classes is not 5")
    sys.exit(1)

#Creamos un fichero out.txt donde se guardaran los resultados, si ya existe lo borramos
lista_de_indices = {}
with open("out.json", "w") as f:
    # Para cada una de las etiquetas, generamos el vector que representa la predicción y valor real que necesita para ser "adcecuada" para explicarla
    for label_idx in range(5):
        #Desired_real es el vector que tiene 1.0 en la posicion label_idx y 0.0 en las demas
        desired_real = np.zeros(5, dtype=np.float32)
        desired_real[label_idx] = 1.0
        desired_predictions = [False, False, False, False, False]
        desired_predictions[label_idx] = True
        desired_predictions = np.asarray(desired_predictions)
        lista_de_indices[label_names[label_idx]] = []
        for i in range(predictions.shape[0]):
            # Para cada predicción, comprobamos si coincide con los arrays de valores deseados
            if np.array_equal(test_y[i], desired_real) and np.array_equal(predictions[i], desired_predictions):
                # Si coincide, guardamos la línea del CSV donde está (que corresponde al índice en el dataset más dos) y el id del ECG
                lista_de_indices[label_names[label_idx]].append({"linea": i + 2, "ecg_id": int(df.iloc[i]['ecg_id'])})
    json.dump(lista_de_indices, f, indent=4)
os.remove("./tmp.npy")