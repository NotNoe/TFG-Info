import pandas as pd
import numpy as np
import wfdb
import ast
import ecg_plot
from scipy.signal import ShortTimeFFT


path = './ptbxl/'

# load and convert annotation data
Y = pd.read_csv(path+'ptbxl_database.csv', index_col='ecg_id')

signals, fields = wfdb.rdsamp(path+'records100/00000/00001_lr')
signals = np.array(signals)
ecg_plot.plot(ecg=signals.transpose(), sample_rate=100, lead_index=fields['sig_name'], show_lead_name=True, show_grid=False, show_separate_line=True,title="ECG a 100Hz")
ecg_plot.show()
#ecg_plot.save_as_png("ecg100", "./out/")

signals, fields = wfdb.rdsamp(path+'records500/00000/00001_hr')
signals = np.array(signals)
ecg_plot.plot(ecg=signals.transpose(), sample_rate=100, lead_index=fields['sig_name'], show_lead_name=True, show_grid=False, show_separate_line=True,title="ECG a 500Hz")
ecg_plot.show()
#ecg_plot.save_as_png("ecg500", "./out/")