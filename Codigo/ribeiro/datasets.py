import h5py
import math
import pandas as pd
from tensorflow.keras.utils import Sequence
import numpy as np


class ECGSequence(Sequence):
    @classmethod
    def get_train_and_val(cls, path_to_hdf5_train, path_to_hdf5_val, hdf5_dset, path_to_csv_train, path_to_csv_val, 
                          batch_size=8, labels = None, dataset_labels = 12, fill_with_zeroes=False):
        train_seq = cls(path_to_hdf5_train, hdf5_dset, path_to_csv_train, batch_size, labels = labels, dataset_labels = dataset_labels, fill_with_zeroes=fill_with_zeroes)
        valid_seq = cls(path_to_hdf5_val, hdf5_dset, path_to_csv_val, batch_size, labels = labels, dataset_labels = dataset_labels, fill_with_zeroes=fill_with_zeroes)
        return train_seq, valid_seq


    def __init__(self, path_to_hdf5, hdf5_dset, path_to_csv=None, batch_size=8,
                 start_idx=0, end_idx=None, labels = None, dataset_labels = 12, fill_with_zeroes=False):
        if path_to_csv is None:
            self.y = None
        else:
            self.y = pd.read_csv(path_to_csv, index_col=0).values
        # Get tracings
        self.f = h5py.File(path_to_hdf5, "r")
        data = self.f[hdf5_dset]
        if labels is None:
            self.x = self.f[hdf5_dset]
        elif fill_with_zeroes:
            M = data.shape[1]
            if M % dataset_labels != 0:
                raise ValueError("The number of labels is not a multiple of dataset_labels")
            block_size = M//dataset_labels
            self.x = self.f[hdf5_dset]
            labels_to_zero = [i for i in range(1, dataset_labels+1) if i not in labels] #Los que no estan en labels
            for i in labels_to_zero:
                start = (i-1)*block_size
                end = i*block_size
                self.x[:,start:end,:] = 0
        else: #En este caso solamente sacamos las que estan en labels
            M = data.shape[1]
            #Si M no es divisible por dataset_labels, hay un error
            if M % dataset_labels != 0:
                raise ValueError("The number of labels is not a multiple of dataset_labels")
            block_size = M//dataset_labels
            submatrices = []
            for i in labels:
                start = (i-1)*block_size
                end = i*block_size
                submatrices.append(data[:,start:end,:])
            self.x = np.concatenate(submatrices, axis=1)
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