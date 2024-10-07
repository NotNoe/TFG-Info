import pandas as pd
import numpy as np
import wfdb
import ast
import ecg_plot
from scipy.signal import ShortTimeFFT
import h5py


path = './ptbxl/'

# load and convert annotation data
#Y = pd.read_csv(path+'ptbxl_database.csv', index_col='ecg_id')
signals = wfdb.rdsamp("./ptbxl/records500/00000/00001_hr")[0].transpose() #Devuelve un array de 5000x12
ecg_plot.plot(signals, sample_rate=500, show_grid=False)
with h5py.File("./ptbxl/records500.hdf5", 'r') as f:
    processed_signals = f['tracings'][0,:,:].transpose()
ecg_plot.plot(processed_signals, sample_rate=400, show_grid=False)
with h5py.File("./ptbxl/recordsnotch.hdf5", 'r') as f:
    processed_signals = f['tracings'][0,:,:].transpose()
ecg_plot.plot(processed_signals, sample_rate=400, show_grid=False)
ecg_plot.show()