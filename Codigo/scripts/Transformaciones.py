from scipy.signal import stft
import numpy as np


FREQ = 400
#Creamos la clase para las transformaciones
class Transformaciones:
    #El constructor recibe los datos, que son una cantidad de matrices de 4096x12
    def __init__(self, ecgs):
        self.ecgs = ecgs
        self.n_cases = ecgs.shape[0]

    def get_stft_arrays(self, nperseg=256, noverlap=128):
        #Calculamos las dimensiones de la matriz de salida usando la primera matriz de entrada
        f, t, _ = stft(self.ecgs[0][:, 0], fs=FREQ, nperseg=nperseg, noverlap=noverlap)
        return f, t

    #Función que realiza la transformada STFT
    def stft(self, nperseg=256, noverlap=128):
        #Calculamos las dimensiones de la matriz de salida usando la primera matriz de entrada
        n_frequencies, n_times = stft(self.ecgs[0][:, 0], fs=FREQ, nperseg=nperseg, noverlap=noverlap)[2].shape
        #Creamos un array vacío para guardar los resultados
        stfts = []
        #Iteramos sobre los datos
        for i in range(self.n_cases):
            ecg = self.ecgs[i]
            stft_i = np.zeros((n_frequencies * ecg.shape[1], n_times))
            for j in range(ecg.shape[1]):
                _, _, Zxx = stft(ecg[:, j], fs=FREQ, nperseg=nperseg, noverlap=noverlap)
                stft_i[j * n_frequencies:(j + 1) * n_frequencies, :] = np.abs(Zxx)
            stfts.append(stft_i)
        return np.array(stfts)
            