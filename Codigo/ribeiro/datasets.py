import h5py
import math
import pandas as pd
from tensorflow.keras.utils import Sequence
import numpy as np


import h5py
import math
import pandas as pd
from tensorflow.keras.utils import Sequence
import numpy as np


class ECGSequence(Sequence):
    @classmethod
    def get_train_and_val(cls, path_to_hdf5_train, path_to_hdf5_val, hdf5_dset, path_to_csv_train, path_to_csv_val, batch_size=8):
        train_seq = cls(path_to_hdf5_train, hdf5_dset, path_to_csv_train, batch_size)
        valid_seq = cls(path_to_hdf5_val, hdf5_dset, path_to_csv_val, batch_size)
        return train_seq, valid_seq


    def __init__(self, path_to_hdf5, hdf5_dset, path_to_csv=None, batch_size=8,
                 start_idx=0, end_idx=None):
        if path_to_csv is None:
            self.y = None
        else:
            self.y = pd.read_csv(path_to_csv, index_col=0).values
        # Get tracings
        self.f = h5py.File(path_to_hdf5, "r")
        self.x = self.f[hdf5_dset]
        self.batch_size = batch_size
        if end_idx is None:
            end_idx = len(self.x)
        self.start_idx = start_idx
        self.end_idx = end_idx

    @property
    def n_classes(self):
        return self.y.shape[1]

    def __getitem__(self, idx):
        start = self.start_idx + idx * self.batch_size
        end = min(start + self.batch_size, self.end_idx)
        if self.y is None:
            return np.array(self.x[start:end, :, :]).astype(np.float32)
        else:
            return np.array(self.x[start:end, :, :]).astype(np.float32), np.array(self.y[start:end])

    def __len__(self):
        return math.ceil((self.end_idx - self.start_idx) / self.batch_size)

    def __del__(self):
        try:
            self.f.close()
        except Exception:
            pass