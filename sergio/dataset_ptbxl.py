import ast
import numpy as np
import pandas as pd
import wfdb

# path: el que está puesto es el que funciona si los datos están en una carpeta llamada ptbxl
# situada en el primer nivel, junto con src y utils
# sampling rate: 500 Hz o 100 Hz (downsampled)
# test_fold: 1-10 (for cross validation)

class Ptbxl_dataset():
    # carga los datos en memoria
    def __init__(self, path='../../Data/ptbxl/', sampling_rate=500):
        # load and convert annotation data
        self.Y = pd.read_csv(path+'ptbxl_database.csv', index_col='ecg_id')
        # de string a dic
        self.Y.scp_codes = self.Y.scp_codes.apply(lambda x: ast.literal_eval(x))
        # Load scp_statements.csv for diagnostic aggregation (no sé si esta es la etiqueta que queremos)
        agg_df = pd.read_csv(path+'scp_statements.csv', index_col=0)
        agg_df = agg_df[agg_df.diagnostic == 1]
        def aggregate_diagnostic(y_dic):
            tmp = []
            for key in y_dic.keys():
                if key in agg_df.index:
                    tmp.append(agg_df.loc[key].diagnostic_class)
            return list(set(tmp))
        # Apply diagnostic superclass
        self.Y['diagnostic_superclass'] = self.Y.scp_codes.apply(aggregate_diagnostic)

        # Load raw signal data
        if sampling_rate == 100:
            data = [wfdb.rdsamp(path+f) for f in self.Y.filename_lr]
        else:
            data = [wfdb.rdsamp(path+f) for f in self.Y.filename_hr]
        self.X = np.array([signal for signal, meta in data])
        

    # devuelve los datos de train y test divididos de acuerdo a test_fold (1-10)
    def get_data_split(self, test_fold=10):
        # Split data into train and test
        # Train
        X_train = self.X[np.where(self.Y.strat_fold != test_fold)]
        y_train = self.Y[(self.Y.strat_fold != test_fold)].diagnostic_superclass.to_numpy()
        # Test
        X_test = self.X[np.where(self.Y.strat_fold == test_fold)]
        y_test = self.Y[self.Y.strat_fold == test_fold].diagnostic_superclass.to_numpy()
        return (X_train, y_train), (X_test, y_test)
    
    def one_hot_encode(self, y, classes):
        y = np.array([np.array([1 if c in sample else 0 for c in classes]) for sample in y])
        return y