import json
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import h5py
import pandas as pd
import sys
from tensorflow.keras.models import load_model

label_names = ["CD", "HYP", "MI", "NORM", "STTC"]

#Load the datasets
test_x = h5py.File('./data/test.hdf5', 'r')["tracings"]
# Load the labels from the CSV file
df = pd.read_csv('./data/test_db.csv')
test_y = df.drop(columns=['ecg_id']).to_numpy()

#Exec predict.py from ribeiro folder
os.system("python ./ribeiro/predict.py data/test.hdf5 final_models/original_model.hdf5 --output_file ./tmp.npy --dataset_name tracings")
predictions = np.load("./tmp.npy")
#Convertimos predictions a un array de booleanos mediante el threshold 0.5
predictions = predictions > 0.5
if predictions.shape[0] != test_y.shape[0]:
    print("The number of test samples and predictions do not match")
    sys.exit(1)
if predictions.shape[1] != test_y.shape[1] or predictions.shape[1] != 5:
    print("The number of classes is not 5")
    sys.exit(1)
#Creamos un fichero out.txt donde se guardaran los resultados, si ya existe lo borramos
lista_de_indices = {}
with open("out.json", "w") as f:
    for label_idx in range(5):
        #Desired_real es el vector que tiene 1.0 en la posicion label_idx y 0.0 en las demas
        desired_real = np.zeros(5, dtype=np.float32)
        desired_real[label_idx] = 1.0
        desired_predictions = [False, False, False, False, False]
        desired_predictions[label_idx] = True
        desired_predictions = np.asarray(desired_predictions)
        lista_de_indices[label_names[label_idx]] = []
        for i in range(predictions.shape[0]):
            if np.array_equal(test_y[i], desired_real) and np.array_equal(predictions[i], desired_predictions):
                lista_de_indices[label_names[label_idx]].append({"linea": i + 2, "ecg_id": int(df.iloc[i]['ecg_id'])})
    json.dump(lista_de_indices, f, indent=4)
os.remove("./tmp.npy")