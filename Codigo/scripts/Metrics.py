import numpy as np
import json
from sklearn.metrics import precision_recall_fscore_support, average_precision_score

class Metrics:
    def __init__(self, y_true, y_pred, threshold=0.5, class_names=None):
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
        if class_names is None:
            self.class_names = [f"class_{i}" for i in range(y_true.shape[1])]
        elif len(class_names) != y_true.shape[1]:
            raise ValueError("El número de nombres de clase debe coincidir con el número de columnas en y_true.")
        else:
            self.class_names = class_names

    def recall(self):
        """ 
        Calcula el Recall por clase y su promedio (Macro Recall).
        
        - Qué significa: Mide la proporción de verdaderos positivos identificados correctamente para cada clase individualmente.
        - Contexto de uso: Útil para entender el rendimiento del modelo en cada clase específica.
        - Interpretación: Retorna un arreglo con el recall por clase y el promedio de recall.
        """
        _, recall_per_class, _, _ = precision_recall_fscore_support(
            self.y_true, self.y_pred, average=None
        )
        recall_avg = np.mean(recall_per_class)
        return recall_per_class, recall_avg


    def f2_score(self):
        """ 
        Calcula el F2 Score por clase y su promedio.
        
        - Qué significa: Mide el equilibrio entre precisión y recall para cada clase, dando más peso al recall.
        - Contexto de uso: Útil para evaluar el rendimiento en cada clase y entender en cuáles el modelo tiene dificultades.
        - Interpretación: Retorna un arreglo con el F2-Score por clase y el promedio de F2-Score.
        """
        _, _, f2_per_class, _ = precision_recall_fscore_support(
            self.y_true, self.y_pred, average=None, beta=2
        )
        f2_avg = np.mean(f2_per_class)
        return f2_per_class, f2_avg


    def auc_pr(self):
        """ 
        Calcula el AUC-PR por clase y su promedio.
        
        - Qué significa: Mide el área bajo la curva de precisión-recall para cada clase individualmente.
        - Contexto de uso: Útil para evaluar la capacidad del modelo para detectar positivos en cada clase.
        - Interpretación: Retorna un arreglo con el AUC-PR por clase y el promedio de AUC-PR.
        """
        auc_pr_per_class = average_precision_score(
            self.y_true, self.y_pred_prob, average=None
        )
        auc_pr_avg = np.mean(auc_pr_per_class)
        return auc_pr_per_class, auc_pr_avg


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
    
    def f1_score(self):
        """ 
        Calcula el F1 Score por clase y su promedio.
        
        - Qué significa: Mide el equilibrio entre precisión y recall para cada clase.
        - Contexto de uso: Útil para evaluar el rendimiento de cada clase, especialmente en casos con datos desbalanceados.
        - Interpretación: Retorna un arreglo con el F1-Score por clase y el promedio de F1-Score.
        """
        _, _, f1_per_class, _ = precision_recall_fscore_support(
            self.y_true, self.y_pred, average=None
        )
        f1_avg = np.mean(f1_per_class)
        return f1_per_class, f1_avg
    
    def precision(self):
        """ 
        Calcula la Precisión por clase y su promedio.
        
        - Qué significa: Mide la proporción de verdaderos positivos entre todas las predicciones positivas para cada clase.
        - Contexto de uso: Útil para entender la capacidad del modelo para evitar falsos positivos en cada clase.
        - Interpretación: Retorna un arreglo con la precisión por clase y el promedio de precisión.
        """
        precision_per_class, _, _, _ = precision_recall_fscore_support(
            self.y_true, self.y_pred, average=None
        )
        precision_avg = np.mean(precision_per_class)
        return precision_per_class, precision_avg


    
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
        """ 
        Guarda todas las métricas calculadas en un archivo JSON.

        - Incluye las métricas por clase y sus promedios.
        """
        # Obtener métricas y sus promedios
        recall_per_class, recall_avg = self.recall()
        f2_per_class, f2_avg = self.f2_score()
        f1_per_class, f1_avg = self.f1_score()
        precision_per_class, precision_avg = self.precision()
        auc_pr_per_class, auc_pr_avg = self.auc_pr()

        # Crear diccionarios para las métricas por clase usando los nombres de las clases
        recall_dict = {self.class_names[i]: recall_per_class[i] for i in range(len(self.class_names))}
        recall_dict["average"] = recall_avg

        f2_dict = {self.class_names[i]: f2_per_class[i] for i in range(len(self.class_names))}
        f2_dict["average"] = f2_avg

        f1_dict = {self.class_names[i]: f1_per_class[i] for i in range(len(self.class_names))}
        f1_dict["average"] = f1_avg

        precision_dict = {self.class_names[i]: precision_per_class[i] for i in range(len(self.class_names))}
        precision_dict["average"] = precision_avg

        auc_pr_dict = {self.class_names[i]: auc_pr_per_class[i] for i in range(len(self.class_names))}
        auc_pr_dict["average"] = auc_pr_avg

        # Obtener Recall@k y Coverage Error
        recall_at_k = self.recall_at_k_all()
        coverage_error = self.coverage_error()

        # Crear el diccionario final de métricas
        metrics_dict = {
            "recall": recall_dict,
            "precision": precision_dict,
            "f1_score": f1_dict,
            "f2_score": f2_dict,
            "auc_pr": auc_pr_dict,
            "recall_at_k": recall_at_k,
            "coverage_error": coverage_error
        }

        # Guardar en un archivo JSON
        with open(path, 'w') as json_file:
            json.dump(metrics_dict, json_file, indent=4)
