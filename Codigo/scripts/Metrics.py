import numpy as np
import json
from sklearn.metrics import precision_recall_fscore_support, average_precision_score

class Metrics:
    def __init__(self, y_true, y_pred, threshold=0.5):
        """
        Inicializa la clase Metrics con matrices de etiquetas reales y predicciones.
        
        Parameters:
        y_true (np.ndarray): Array de valores reales (ground truth).
        y_pred (np.ndarray): Array de predicciones.
        threshold (float): Umbral para binarizar las predicciones de probabilidad.
        """
        self.y_true = (y_true >= threshold).astype(int)  # Binariza según el umbral
        self.y_pred = (y_pred >= threshold).astype(int)
        self.y_true_prob = y_true
        self.y_pred_prob = y_pred

    def recall(self):
        """ 
        Calcula el Recall promedio (Micro Recall). Mide la proporción de verdaderos positivos identificados correctamente entre todas las etiquetas verdaderas.
        Un valor alto de recall indica que el modelo está capturando la mayoría de las etiquetas relevantes, reduciendo falsos negativos.
        """
        _, recall, _, _ = precision_recall_fscore_support(self.y_true, self.y_pred, average='micro')
        return recall

    def f2_score(self):
        """Calcula el F2 Score promedio, priorizando el recall. Variación del F1-Score que da más peso al recall que a la precisión.
        Un valor alto indica un buen balance entre precisión y recall, con énfasis en reducir falsos negativos.
        """
        _, _, f2, _ = precision_recall_fscore_support(self.y_true, self.y_pred, average='micro', beta=2)
        return f2

    def auc_pr(self):
        """
        Calcula el AUC-PR promedio por clase. Mide el área bajo la curva de precisión-recall, útil para evaluar modelos con datos desbalanceados.
        Un valor alto indica que el modelo tiene buena capacidad de detección de verdaderos positivos en el contexto de desbalance.
        """
        return average_precision_score(self.y_true, self.y_pred_prob, average='micro')

    def recall_at_k(self, k=2):
        """ 
        Calcula Recall@k para cada muestra, ignorando muestras sin etiquetas verdaderas.
        Mide la proporción de verdaderas etiquetas entre las k etiquetas más probables.
        Un valor alto indica que el modelo captura las etiquetas relevantes en sus predicciones principales.
        """
        total_recall = 0
        valid_samples = 0  # Contador de muestras con al menos una etiqueta verdadera
        for i in range(len(self.y_true)):
            true_labels_count = np.sum(self.y_true[i])
            if true_labels_count == 0:
                continue  # Ignora muestras sin etiquetas verdaderas
            
            top_k_preds = np.argsort(-self.y_pred_prob[i])[:k]
            total_recall += np.sum(self.y_true[i, top_k_preds]) / true_labels_count
            valid_samples += 1

        return total_recall / valid_samples if valid_samples > 0 else 0
    
    def recall_at_k_all(self):
        """ 
        Calcula Recall@k para todos los valores de k entre 1 y el total de etiquetas y los devuelve como un diccionario.
        Mide el recall para cada valor de k. Cuanto antes crezca el recall, menos etiquetas necesita para capturar las verdaderas.
        Devuelve un diccionario con recall para cada k, que muestra cómo varía el recall en distintos valores de k.
        """
        recall_at_k_values = {}
        recall_at_k_values = {f"{k}": self.recall_at_k(k) for k in range(1, self.y_true_prob.shape[1])}
        return recall_at_k_values
    
    def coverage_error(self):
        """ 
        - Qué significa: Mide en promedio cuántas etiquetas necesita recorrer el modelo para cubrir todas las etiquetas verdaderas, normalizado por el número de verdaderos positivos de cada muestra.
        - Contexto de uso: Útil para entender el esfuerzo relativo del modelo para cubrir todas las etiquetas verdaderas en cada muestra, especialmente cuando las muestras tienen diferentes cantidades de verdaderos positivos.
        - Interpretación: Un valor bajo indica que el modelo puede capturar los verdaderos positivos rápidamente en las primeras posiciones.
        """
        coverage = 0
        valid_samples = 0  # Contador de muestras con al menos una etiqueta verdadera
        for i in range(len(self.y_true)):
            true_labels = np.where(self.y_true[i] == 1)[0]
            if len(true_labels) == 0:
                continue  # Ignora muestras sin etiquetas verdaderas
            
            sorted_pred = np.argsort(-self.y_pred_prob[i])
            # Calcula la cobertura necesaria para capturar todas las etiquetas verdaderas y normaliza
            max_index = np.where(np.isin(sorted_pred, true_labels))[0].max() + 1
            coverage += max_index / len(true_labels)
            valid_samples += 1

        return coverage / valid_samples if valid_samples > 0 else 0

    def dump_to_json(self, path):
        """Guarda todas las métricas calculadas en un archivo JSON."""
        metrics_dict = {
            "recall": self.recall(),
            "f2_score": self.f2_score(),
            "auc_pr": self.auc_pr(),
            "recall_at_k": self.recall_at_k_all(),
            "coverage_error": self.coverage_error()
        }
        with open(path, 'w') as json_file:
            json.dump(metrics_dict, json_file, indent=4)