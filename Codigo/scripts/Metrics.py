import numpy as np
import json
from sklearn.metrics import precision_recall_fscore_support, fbeta_score

class Metrics:
    def __init__(self, y_true, y_pred, class_names=None):
        """
        Inicializa la clase Metrics con matrices de etiquetas reales y predicciones.

        Parameters:
        y_true (np.ndarray): Array de valores reales (probabilidades entre 0 y 1).
                             Dimensión: (n_samples, n_classes)
        y_pred (np.ndarray): Array de predicciones (probabilidades entre 0 y 1).
                             Dimensión: (n_samples, n_classes)
        class_names (list, opcional): Lista con los nombres de las clases.
                                      Longitud: n_classes
        """
        self.y_true_prob = y_true
        self.y_pred_prob = y_pred
        self.class_names = class_names
        self.n_classes = y_true.shape[1]

        # Binarizar las etiquetas reales y predichas usando un umbral de 0.5
        self.y_true = (self.y_true_prob >= 0.5).astype(int)
        self.y_pred = (self.y_pred_prob >= 0.5).astype(int)

        # Verificar si alguna clase no tiene representantes en y_true
        self.classes_with_no_samples = []
        for i in range(self.n_classes):
            y_true_sum = np.sum(self.y_true[:, i])
            if y_true_sum == 0:
                if self.class_names:
                    class_name = self.class_names[i]
                else:
                    class_name = f'Clase_{i}'
                self.classes_with_no_samples.append(class_name)

        if self.classes_with_no_samples:
            print(f"Advertencia: Las siguientes clases no tienen representantes en la muestra de test: {', '.join(self.classes_with_no_samples)}")

    def calculate_precision_recall_f1(self):
        """
        Calcula las métricas de precisión, recall y F1-score para cada clase y de manera global.

        Returns:
        dict: Diccionario con las métricas calculadas.
        """
        precision_dict = {}
        recall_dict = {}
        f1_dict = {}
        
        precision_list, recall_list, f1_list, _ = precision_recall_fscore_support(self.y_true, self.y_pred, zero_division=np.nan)
        for i in range(self.n_classes): #Para cada clase
            if self.class_names:
                class_name = self.class_names[i]
            else:
                class_name = f'Clase_{i}'
            precision_dict[class_name] = precision_list[i]
            recall_dict[class_name] = recall_list[i]
            f1_dict[class_name] = f1_list[i]


        global_precision, global_recall, global_f1, _ = precision_recall_fscore_support(self.y_true, self.y_pred, average='micro', zero_division=np.nan)

        metrics = {
            'precision': {
                'by_class': precision_dict,
                'global_average': global_precision
            },
            'recall': {
                'by_class': recall_dict,
                'global_average': global_recall
            },
            'f1_score': {
                'by_class': f1_dict,
                'global_average': global_f1
            }
        }

        return metrics

    def calculate_adjusted_f_score(self):
        """
        Calcula la métrica personalizada 'adjusted_f_score' combinando F0.5 para 'NORM' y F2 para las demás clases.

        Returns:
        float or None: Valor de la métrica personalizada.
        """
        if self.class_names is None:
            clase_especial = 3
            print("Warning: No se han proporcionado los nombres de las clases. Se asumirá que la clase NORM es la clase 3.")
        else:
            clase_especial = self.class_names.index('NORM')
        metricas = []
        for cls in range(self.n_classes):
            if cls == clase_especial:
                beta = 0.5
            else:
                beta = 2
            f_score = fbeta_score(self.y_true[:,cls], self.y_pred[:,cls], beta=beta)
            metricas.append(f_score)
        adjusted_f_score = np.mean(metricas)

        return adjusted_f_score

    def dump_to_json(self, path):
        """
        Escribe las métricas calculadas en un archivo JSON.

        Parameters:
        path (str): Ruta al archivo JSON de salida.
        """
        # Crear un diccionario ordenado para asegurar el orden de las métricas
        metrics = {}

        # Calcular la métrica personalizada y agregarla primero
        adjusted_f_score = self.calculate_adjusted_f_score()
        metrics['adjusted_f_score'] = adjusted_f_score

        # Calcular las demás métricas
        prf_metrics = self.calculate_precision_recall_f1()
        metrics.update(prf_metrics)

        # Escribir en el archivo JSON
        with open(path, 'w') as json_file:
            json.dump(metrics, json_file, indent=4)
