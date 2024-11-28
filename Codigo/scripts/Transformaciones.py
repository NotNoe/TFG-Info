from scipy.signal import stft, cwt, ricker, morlet2
import numpy as np

FREQ = 400
#Creamos la clase para las transformaciones
class Transformaciones:
    #El constructor recibe los datos, que son una cantidad de matrices de 4096x12
    def __init__(self, ecgs):
        self.ecgs = ecgs
        self.n_cases = ecgs.shape[0]


    def get_cwt_arrays(self, wavelet = ricker, scales = np.linspace(1,128,300)):  
        #Calculamos las dimensiones de la matriz de salida usando la primera matriz de entrada
        if wavelet == ricker:
            f = FREQ / (2*np.pi*scales)
        elif wavelet == morlet2:
            f = (5 * FREQ) / (2 * np.pi * scales)
        else:
            raise NotImplementedError("Wavelet no reconocido")

        t = np.arange(self.ecgs[0].shape[0]) / FREQ
        return f,t

    def cwt(self, wavelet = ricker, scales = np.linspace(1,128, 300)):  
        cwts = []
        for i in range(self.n_cases):
            ecg = self.ecgs[i]
            cwt_i = np.zeros((len(scales) * ecg.shape[1], ecg.shape[0]))
            for j in range(ecg.shape[1]): #Iteramos sobre las derivaciones
                Zxx = np.abs(cwt(ecg[:,j], wavelet=wavelet, widths=scales))
                cwt_i[j * len(scales):(j + 1) * len(scales), :] = Zxx
            cwts.append(cwt_i)
        return np.array(cwts)

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
            