import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns

CLASSES = 6

class Metrics:
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray):
        """
        Constructor que recibe las probabilidades reales y las predichas para cada clase.
        
        :param y_true: np.ndarray con las probabilidades reales para cada clase.
        :param y_pred: np.ndarray con las probabilidades predichas para cada clase.
        """
        self.y_true = np.argmax(y_true, axis=1)
        self.y_pred = np.argmax(y_pred, axis=1)
        self.num_classes = CLASSES
    
    def accuracy(self) -> float:
        """
        Calcula y devuelve la precisión (accuracy) basada en la selección de la clase con mayor probabilidad.
        :return: float con la precisión.
        """
        correct_predictions = np.sum(self.y_true == self.y_pred)
        return correct_predictions / len(self.y_true)
    
    def precision(self) -> float:
        """
        Calcula la precisión macro (precision) del clasificador.
        :return: float con la precisión.
        """
        precisions = []
        for class_id in range(self.num_classes):
            true_positives = np.sum((self.y_pred == class_id) & (self.y_true == class_id))
            predicted_positives = np.sum(self.y_pred == class_id)
            precision = true_positives / predicted_positives if predicted_positives > 0 else 0
            precisions.append(precision)
        return np.mean(precisions)
    
    def recall(self) -> float:
        """
        Calcula el recall macro del clasificador.
        :return: float con el recall.
        """
        recalls = []
        for class_id in range(self.num_classes):
            true_positives = np.sum((self.y_pred == class_id) & (self.y_true == class_id))
            actual_positives = np.sum(self.y_true == class_id)
            recall = true_positives / actual_positives if actual_positives > 0 else 0
            recalls.append(recall)
        return np.mean(recalls)
    
    def f1(self) -> float:
        """
        Calcula y devuelve el F1-score macro del clasificador.
        :return: float con el F1-score.
        """
        precisions = []
        recalls = []
        for class_id in range(self.num_classes):
            true_positives = np.sum((self.y_pred == class_id) & (self.y_true == class_id))
            predicted_positives = np.sum(self.y_pred == class_id)
            actual_positives = np.sum(self.y_true == class_id)
            
            precision = true_positives / predicted_positives if predicted_positives > 0 else 0
            recall = true_positives / actual_positives if actual_positives > 0 else 0
            
            precisions.append(precision)
            recalls.append(recall)
        
        f1_scores = []
        for precision, recall in zip(precisions, recalls):
            if precision + recall == 0:
                f1 = 0
            else:
                f1 = 2 * (precision * recall) / (precision + recall)
            f1_scores.append(f1)
        
        return np.mean(f1_scores)
    
    def confusion_matrix(self) -> np.ndarray:
        """
        Calcula y devuelve la matriz de confusión basada en las clases más probables.
        :return: np.ndarray con la matriz de confusión.
        """
        cm = np.zeros((self.num_classes, self.num_classes), dtype=int)
        for true_class, pred_class in zip(self.y_true, self.y_pred):
            cm[true_class, pred_class] += 1
        return cm

    def plot_confusion_matrix(self):
        """
        Dibuja la matriz de confusión utilizando seaborn.
        """
        cm = self.confusion_matrix()
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted Class')
        plt.ylabel('True Class')
        plt.title('Confusion Matrix')
        plt.show()

    def dump_to_json(self, filename: str):
        """
        Guarda las estadísticas del clasificador en un archivo JSON.
        
        :param filename: Nombre del archivo JSON de salida.
        """
        metrics_data = {
            "accuracy": self.accuracy(),
            "precision_macro": self.precision(),
            "recall_macro": self.recall(),
            "f1_macro": self.f1(),
            "confusion_matrix": self.confusion_matrix().tolist()
        }
        
        with open(filename, 'w') as f:
            json.dump(metrics_data, f, indent=4)
