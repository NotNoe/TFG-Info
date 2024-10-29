import h5py
from tqdm import tqdm
from Transformaciones import Transformaciones

destiny_dataset = "stft"
BATCH = 1000
files = ["data/train.hdf5", "data/test.hdf5", "data/validation.hdf5"]
for filename in files:
    #Abrimos el archivo y sacamos todos los datos en batches de 1000
    with h5py.File(filename, 'r+') as file:
        ecgs = file['tracings']
        f, t = Transformaciones(ecgs[0:1]).get_stft_arrays()
        n_ecgs = ecgs.shape[0]
        #Si el dataset existe, lo borramos
        if destiny_dataset in file:
            del file[destiny_dataset]
        procesed = file.create_dataset(destiny_dataset, shape=(n_ecgs, len(f) * 12, len(t)), dtype='float32')
        for i in tqdm(range(0, n_ecgs, BATCH), "Procesando el archivo " + filename):
            end = min(i + BATCH, n_ecgs)
            batch_ecgs = ecgs[i:end,:,:]
            transformaciones = Transformaciones(batch_ecgs)
            transformed_ecg = transformaciones.stft()
            procesed[i:end] = transformed_ecg


            