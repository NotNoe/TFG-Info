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
        self.labes = labels
        self.dataset_labels = dataset_labels
        self.fill_with_zeroes = fill_with_zeroes
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
        batch_x = np.array(self.x[start:end, :, :]).astype(np.float32)
        if self.labels is not None and self.fill_with_zeroes:
            M = batch_x.shape[1]
            if M % self.dataset_labels != 0:
                raise ValueError("The number of labels is not a multiple of dataset_labels")
            block_size = M//self.dataset_labels
            labels_to_zero = [i for i in range(1, self.dataset_labels+1) if i not in self.labels]
            for i in labels_to_zero:
                start = (i-1)*block_size
                end = i*block_size
                batch_x[:,start:end,:] = 0
        elif self.labels is not None and not self.fill_with_zeroes:
            M = batch_x.shape[1]
            if M % self.dataset_labels != 0:
                raise ValueError("The number of labels is not a multiple of dataset_labels")
            block_size = M//self.dataset_labels
            selected_blocs = []
            for label_id in self.labels:
                start = (label_id-1)*block_size
                end = label_id*block_size
                selected_blocs.append(batch_x[:,start:end,:])
            batch_x = np.concatenate(selected_blocs, axis=1)
        if self.y is None:
            return batch_x
        else:
            return batch_x, np.array(self.y[start:end])

    def __len__(self):
        return math.ceil((self.end_idx - self.start_idx) / self.batch_size)

    def __del__(self):
        try:
            self.f.close()
        except Exception:
            pass