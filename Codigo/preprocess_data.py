import csv
import pandas as pd
import ast
import os

#load anotations and raw data
Y = pd.read_csv('./ptbxl/ptbxl_database.csv', index_col='ecg_id')
Y.scp_codes = Y.scp_codes.apply(lambda x: ast.literal_eval(x))
Y = pd.DataFrame(Y, columns=['scp_codes', 'strat_fold', 'filename_hr'])
Y = Y.rename(columns={'filename_hr':'filename'})
validation_fold = 9
test_fold = 10
Y_train = Y[(Y.strat_fold != validation_fold) & (Y.strat_fold != test_fold)].drop(columns=['strat_fold'])
Y_validation = Y[Y.strat_fold == validation_fold].drop(columns=['strat_fold'])
Y_test = Y[Y.strat_fold == test_fold].drop(columns=['strat_fold'])

with open("./data/train_REC", 'w+') as f:
    for index, row in Y_train.iterrows():
        f.write(row['filename'] + "\n")
    Y_train.to_csv("./data/train_db.csv")

with open("./data/validation_REC", 'w+') as f:
    for index, row in Y_validation.iterrows():
        f.write(row['filename'] + "\n")
    Y_validation.to_csv("./data/validation_db.csv")

with open("./data/test_REC", 'w+') as f:
    for index, row in Y_test.iterrows():
        f.write(row['filename'] + "\n")
    Y_test.to_csv("./data/test_db.csv")

os.system("python3 ./sergio/generate_h5.py ./data/test_REC ./data/test.hdf5 --root_dir ./ptbxl")
os.system("python3 ./sergio/generate_h5.py ./data/train_REC ./data/train.hdf5 --root_dir ./ptbxl")
os.system("python3 ./sergio/generate_h5.py ./data/validation_REC ./data/validation.hdf5 --root_dir ./ptbxl")

