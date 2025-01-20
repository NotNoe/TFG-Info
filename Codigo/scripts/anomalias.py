import ecg_plot
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import h5py

matplotlib.use('Agg')
ids = {"CD": 24, "MI": 70, "STTC": 21, "NORM": 2, "HYP": 225}
os.makedirs(f"./out/ecg_clases", exist_ok=True)
for clase in ["CD", "HYP", "MI", "NORM", "STTC"]:
    if clase != "HYP":
        #Genera un string a partir de un número asegurando que tiene 5 digitos
        path = "./ptbxl/records500/00000/" + str(ids[clase]).zfill(5) + "_hr"
    else:
        path = "./ptbxl/records500/01000/" + str(ids[clase]).zfill(5) + "_hr"
    with h5py.File("data/test.hdf5", 'r') as file:
        signals = file["tracings"][ids[clase]-2].T
    ecg_plot.plot(signals, sample_rate=400, title=f"Clase: {clase}")
    fig = plt.gcf()
    for ax in fig.get_axes():
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)  # Oculta números del eje X
        ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)  # Oculta números del eje Y
    ecg_plot.save_as_png(f"./out/ecg_clases/{clase}")