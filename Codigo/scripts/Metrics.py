import numpy as np
import json
from sklearn.metrics import precision_recall_fscore_support

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
        self.metrics_dict = {}

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
        """
        precision_dict = {}
        recall_dict = {}
        f1_dict = {}
        precision_list = []
        recall_list = []
        f1_list = []

        for i in range(self.n_classes):
            if self.class_names:
                class_name = self.class_names[i]
            else:
                class_name = f'Clase_{i}'

            y_true_class = self.y_true[:, i]
            y_pred_class = self.y_pred[:, i]

            if class_name in self.classes_with_no_samples:
                precision = None
                recall = None
                f1 = None
            else:
                precision, recall, f1, _ = precision_recall_fscore_support(
                    y_true_class, y_pred_class, average='binary', zero_division=0)

                precision_list.append(precision)
                recall_list.append(recall)
                f1_list.append(f1)

            precision_dict[class_name] = precision
            recall_dict[class_name] = recall
            f1_dict[class_name] = f1

        # Calcular promedios globales (ignorando valores None)
        global_precision = np.mean([p for p in precision_list if p is not None]) if precision_list else None
        global_recall = np.mean([r for r in recall_list if r is not None]) if recall_list else None
        global_f1 = np.mean([f for f in f1_list if f is not None]) if f1_list else None

        self.metrics_dict['precision'] = {
            'by_class': precision_dict,
            'global_average': global_precision
        }
        self.metrics_dict['recall'] = {
            'by_class': recall_dict,
            'global_average': global_recall
        }
        self.metrics_dict['f1_score'] = {
            'by_class': f1_dict,
            'global_average': global_f1
        }

    def calculate_custom_metric(self):
        """
        Calcula la métrica personalizada combinando F0.5 para 'NORM' y F2 para las demás clases.
        """
        if not self.class_names:
            print("Advertencia: No se proporcionaron nombres de clases. No se puede calcular la métrica personalizada.")
            self.metrics_dict['custom_metric'] = None
            return

        custom_metric_values = []
        for i in range(self.n_classes):
            class_name = self.class_names[i]
            y_true_class = self.y_true[:, i]
            y_pred_class = self.y_pred[:, i]

            if class_name in self.classes_with_no_samples:
                metric_value = None
            else:
                if class_name == 'NORM':
                    _, _, metric_value, _ = precision_recall_fscore_support(
                        y_true_class, y_pred_class, average='binary', beta=0.5, zero_division=0)
                else:
                    _, _, metric_value, _ = precision_recall_fscore_support(
                        y_true_class, y_pred_class, average='binary', beta=2, zero_division=0)

            if metric_value is not None:
                custom_metric_values.append(metric_value)

        if custom_metric_values:
            custom_metric = np.mean(custom_metric_values)
        else:
            custom_metric = None

        self.metrics_dict['custom_metric'] = custom_metric

    def dump_to_json(self, path):
        """
        Escribe las métricas calculadas en un archivo JSON.

        Parameters:
        path (str): Ruta al archivo JSON de salida.
        """
        self.calculate_precision_recall_f1()
        self.calculate_custom_metric()

        with open(path, 'w') as json_file:
            json.dump(self.metrics_dict, json_file, indent=4)