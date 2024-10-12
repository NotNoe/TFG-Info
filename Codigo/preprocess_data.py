import csv
import pandas as pd
import ast
import os

#load anotations and raw data
Y = pd.read_csv('./ptbxl/ptbxl_database.csv', index_col='ecg_id')
Y.scp_codes = Y.scp_codes.apply(lambda x: ast.literal_eval(x))
Y = Y[['scp_codes', 'filename_hr', 'strat_fold']]
Y = Y.rename(columns={'filename_hr':'filename'})
validation_fold = 9
test_fold = 10
Y_train = Y[(Y.strat_fold != validation_fold) & (Y.strat_fold != test_fold)].drop(columns=['strat_fold'])
Y_validation = Y[Y.strat_fold == validation_fold].drop(columns=['strat_fold'])
Y_test = Y[Y.strat_fold == test_fold].drop(columns=['strat_fold'])
scp_statements = pd.read_csv('./ptbxl/scp_statements.csv', index_col=0)[['diagnostic_class']]
super_classes = set(scp_statements['diagnostic_class'].unique())
super_classes = {cls for cls in super_classes if pd.notna(cls)}
super_classes.add('OTHER')

def fill_columns(row:pd.Series) -> pd.Series:
    if isinstance(row['scp_codes'], str):
    # Reemplazar comillas simples por dobles y convertir a diccionario
        cadena_json = row['scp_codes'].replace("'", '"')
        try:
            dict_probs = ast.literal_eval(cadena_json)
        except (ValueError, SyntaxError) as e:
            print(f"Error al convertir la fila {index}: {e}")
            return
    elif isinstance(row['scp_codes'], dict):
        dict_probs = row['scp_codes']
    else:
        print(f"Tipo inesperado en la fila {index}: {type(row['scp_codes'])}")
        raise NotImplementedError("Tipo no reconocido")
    #dict_probs ahora es lo que queremos

    for super_class in super_classes:
        n = 0
        acum = 0       
        for diagnosis, prob in dict_probs.items():
            try:
                superclass = scp_statements['diagnostic_class'].loc[diagnosis]
            except KeyError:
                superclass = 'OTHER'
            #Si su superclase coincide
            if superclass != super_class:
                continue
            n += 1
            acum += prob
        if n == 0:
            row[super_class] = 0.0
        else:
            row[super_class] = acum/n
    return row

def generate_diagnostic_probs(x:pd.DataFrame) -> pd.DataFrame:
    for col in super_classes:
        x[col] = None
    x = x.apply(fill_columns, axis=1)
    return x.drop(columns=['scp_codes'])
            
Y_train = generate_diagnostic_probs(Y_train)
Y_validation = generate_diagnostic_probs(Y_validation)
Y_test = generate_diagnostic_probs(Y_test)


with open("./data/train_REC", 'w+') as f:
    for index, row in Y_train.iterrows():
        f.write(row['filename'] + "\n")
    Y_train.drop(columns=['filename']).to_csv("./data/train_db.csv")

with open("./data/validation_REC", 'w+') as f:
    for index, row in Y_validation.iterrows():
        f.write(row['filename'] + "\n")
    Y_validation.drop(columns=['filename']).to_csv("./data/validation_db.csv")

with open("./data/test_REC", 'w+') as f:
    for index, row in Y_test.iterrows():
        f.write(row['filename'] + "\n")
    Y_test.drop(columns=['filename']).to_csv("./data/test_db.csv")

os.system("python3 ./sergio/generate_h5.py ./data/test_REC ./data/test.hdf5 --root_dir ./ptbxl")
os.system("python3 ./sergio/generate_h5.py ./data/train_REC ./data/train.hdf5 --root_dir ./ptbxl")
os.system("python3 ./sergio/generate_h5.py ./data/validation_REC ./data/validation.hdf5 --root_dir ./ptbxl")

