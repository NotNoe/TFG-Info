# Predicción de Riesgo Cardiovascular Explicable Mediante Deep Learning

Este repositorio contiene el código utilizado para el desarrollo de mi TFG.

## Estructura del repositorio
- **final_models**: Contiene los modelos ya entrenados en formato hdf5. El modelo "cwt_morlet", por limitaciones de tamaño en github, está dividido en varias partes. Para recomponerlo simplemente ejecutar el siguiente comando:
    ```bash
    cat final_models/cwt_morlet_model/part_* > final_moddels/cwt_morlet_model.hdf5
    #Para comprobar la integridad del archivo
    sha256sum -c final_models/cwt_morlet_moddel.sha256
    ```
- **ribeiro**: Contiene código del [repositorio de github de ribeiro](https://github.com/antonior92/automatic-ecg-diagnosis).
- **scripts**: Contiene la mayoría de scripts propios que he desarrollado para varias partes del trabajo.
- **sergio**: Contiene varios scripts facilitados por Sergio González Cabeza para el preprocesamiento del trabajo.
- **test**: Contiene los resultados de testing de cada modelo.
- **env.yaml**: El volcado del entorno de conda con el que se ha ejecutado el software.
- **perfects.json**: La salida del script `search_perfects.py`. Contiene la línea y el id de todos los ECGs del subset de testing que son predicciones perfectas para cada clase. Una predicción se considera perfecta si cumple lo siguiente:
    - Tiene valor real de 1.0 para una clase y 0.0 para las demás, es decir, el ECG pertenece exclusivamente a una clase, con un 100% de seguridad.
    - La única etiqueta predicha por el modelo es el de la clase correcta. Es decir, que el modelo ha predicho correctamente que el ECG pertenece exclusivamente a esa clase.
- **TFG.pdf**: El pdf con el trabajo.
