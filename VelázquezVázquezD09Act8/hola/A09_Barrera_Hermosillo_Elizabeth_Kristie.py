# Actividad 9 - Código k-NN
# Categorización de la base de datos de irises de flores con k-NN de k=5, k=3 y k=1

# ASIGNATURA
# María Fernanda López Aramburo
# Sección D02
# Calendario 2026 B

# INTEGRANTES
# ICOM - Barrera Hermosillo Elizabeth Kristie - 220916338
# ICOM -Rodríguez Luna Paulina - 223378663
# ICOM - Velázquez Vazquéz Valeria - 224785718

# Fecha de entrega: 30 de septiembre de 2026

# Importar librerias
import math
from collections import Counter
import csv # csv: leer datos iniciales
from sklearn.model_selection import train_test_split

#abrir/leer archivo.csv
X =[]
Y=[]
with open ("IRIS_PLANT.csv", 'r') as cvs_data:
    # especificar los encabezados
    names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
    read_data = csv.DictReader(cvs_data, fieldnames=names)

    for row in read_data:
        X.append([float(row['sepal_length']), float(row['sepal_width']), float(row['petal_length']), float(row['petal_width'])])
        if 'setosa' in row['species']:
            Y.append(0)
        elif 'versicolor' in row['species']:
            Y.append(1)
        elif 'virginica' in row['species']:
            Y.append(2)

# dividir 80 /20
X_train, X_test, y_train, y_test = train_test_split(X, Y, train_size=0.8, stratify=Y, random_state=800)

class kNN_Model:
    __normalized_X = []
    __predict_Y = []

    def __transpose_initial_data(self, X):
        res = [[]]*len(X[0])
        for row in X:
            for j, cell in enumerate(row):
                res[j].append(cell)
        return res

    # Normalizar los datos de entrenamiento
    def __normalize_data(self, X):
        X = self.__transpose_initial_data(X)

        def normalize_arr(arr):
            v_max = max(arr)
            v_min = min(arr)
            return [(v-v_min)/(v_max-v_min) for v in arr]

        return [normalize_arr(arr) for arr in X]

    # Encontrar las distancias Manhattan de todos los elementos normalizados con respecto a un nuevo punto
    def __calculate_manhattan_for(self, target):
        if(len(target) != len(self.__normalized_X)): 
            raise Exception("Target is not of the same cardinality as data")

        res = [0]*len(self.__normalized_X[0])

        for i, col in enumerate(self.__normalized_X):
            for j, c in enumerate(col):
                res[j]+=abs(target[i] - c)
        
        return res

    # Dadas las distancias de todos los elementos, encontrar los k vecinos más cercanos
    def __get_nearest_neighbors(self, k, distances):
        res = [{"dist": math.inf, "i": -1}]*k
        def insert_new_neighbor(n, i):
            curr = n
            for j in reversed(range(0,i)):
                res[j], curr = curr, res[j]

        for d in distances:
            for i in range(len(res)):
                if(res[i]["dist"] > d): 
                    insert_new_neighbor({"dist":d, "i":i}, i)
                    break
        
        return res

    # Dado el arreglo de tamaño k de los vecinos más cercanos, encontrar la mayoría de votos
    def __get_majority_vote(self, neighbors):
        cnt = Counter()
        for n in neighbors:
            val = self.__predict_Y[n["i"]]
            cnt[val] += 1
        return cnt.most_common()

    # Inicializar el modelo con los datos normalizados en X y las categorías a predecir en Y
    def __init__(self, training_data, predict_data):
        self.__normalized_X = self.__normalize_data(training_data)
        self.__predict_Y = predict_data

    # Una vez preparado el modelo, predecir un nuevo punto mediante los k vecinos más cercanos
    def predict(self, target, k):
        distances = self.__calculate_manhattan_for(target)
        neighbors = self.__get_nearest_neighbors(k, distances)
        return self.__get_majority_vote(neighbors)

knn = kNN_Model(X_train, y_train)

def evaluate_model(model, X_test, Y_test, k):
    """
    Evalúa el modelo k-NN calculando Accuracy, Precision, Recall, Specificity y F1-Score.
    Utiliza Macro-Averaging para manejar las 3 clases del dataset Iris.
    """
    # Obtener las clases únicas del dataset de prueba
    classes = list(set(Y_test))
    
    # Diccionario para almacenar TP, TN, FP, FN de cada clase
    counts = {c: {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0} for c in classes}
    
    correct_predictions = 0
    total_elements = len(X_test)
    
    # 1. Probar cada elemento del arreglo de prueba
    for i in range(total_elements):
        target = X_test[i]
        actual = Y_test[i]
        
        # El método predict retorna Counter.most_common(), ej: [(clase, votos), ...]
        # Tomamos el primer elemento (el más votado) y de ahí extraemos el nombre de la clase [0][0]
        prediction_result = model.predict(target, k)
        prediction = prediction_result[0][0]
        
        if prediction == actual:
            correct_predictions += 1
            
        # 2. Clasificar en TP, TN, FP, FN para CADA clase
        for c in classes:
            if prediction == c and actual == c:
                counts[c]['TP'] += 1
            elif prediction != c and actual != c:
                counts[c]['TN'] += 1
            elif prediction == c and actual != c:
                counts[c]['FP'] += 1
            elif prediction != c and actual == c:
                counts[c]['FN'] += 1

    # 3. Calcular métricas
    sum_precision = 0
    sum_recall = 0
    sum_specificity = 0
    sum_f1 = 0
    
    num_classes = len(classes)
    
    for c in classes:
        TP = counts[c]['TP']
        TN = counts[c]['TN']
        FP = counts[c]['FP']
        FN = counts[c]['FN']
        
        # Evitar divisiones por cero en caso de clases sin ciertas predicciones
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
        
        f1_score = 0
        if (precision + recall) > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
            
        sum_precision += precision
        sum_recall += recall
        sum_specificity += specificity
        sum_f1 += f1_score

    # Calcular los promedios (Macro) y la exactitud (Accuracy) general
    overall_accuracy = correct_predictions / total_elements
    macro_precision = sum_precision / num_classes
    macro_recall = sum_recall / num_classes
    macro_specificity = sum_specificity / num_classes
    macro_f1 = sum_f1 / num_classes
    
    # Imprimir los resultados
    print(f"\n=== Results for k = {k} ===")
    print(f"Accuracy:    {overall_accuracy:.4f}")
    print(f"Precision:   {macro_precision:.4f}")
    print(f"Recall:      {macro_recall:.4f}")
    print(f"Specificity: {macro_specificity:.4f}")
    print(f"F1-Score:    {macro_f1:.4f}")

evaluate_model(knn, X_test, y_test, k=5)
evaluate_model(knn, X_test, y_test, k=3)
evaluate_model(knn, X_test, y_test, k=1)