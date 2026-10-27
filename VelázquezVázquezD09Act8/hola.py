import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ==========================================
# 1. GENERACIÓN DEL ARCHIVO CSV
# ==========================================
print("Generando archivo 'IRIS_PLANT.csv'...")

# Cargar el dataset integrado en scikit-learn
iris = load_iris()

# Crear una tabla con las medidas de las flores
df_generado = pd.DataFrame(data=iris.data, columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])

# Agregar la columna final con el nombre real de la especie
df_generado['species'] = [iris.target_names[i] for i in iris.target]

# Guardarlo como archivo CSV (sin encabezados para compatibilidad con código manual)
df_generado.to_csv('IRIS_PLANT.csv', index=False, header=False)
print("¡Listo! Archivo creado exitosamente.\n")

# ==========================================
# 2. CARGA DE DATOS Y EVALUACIÓN
# ==========================================
print("Iniciando evaluación del modelo con Scikit-Learn...\n")

# Cargar el dataset recién creado
df = pd.read_csv('IRIS_PLANT.csv', header=None)

# Separar características (X) y la clase a predecir (Y)
X = df.iloc[:, :-1].values
Y = df.iloc[:, -1].values

# Dividir en 80% entrenamiento y 20% prueba
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=15)

# Evaluar el modelo para los valores k solicitados
valores_k = [1, 3, 5]

for k in valores_k:
    # Inicializar el clasificador con distancia Manhattan (p=1)
    knn = KNeighborsClassifier(n_neighbors=k, p=1)
    
    # Entrenar el modelo
    knn.fit(X_train, Y_train)
    
    # Predecir con los datos de prueba
    Y_pred = knn.predict(X_test)
    
    # Calcular las métricas (Macro-Averaging para las 3 clases)
    accuracy = accuracy_score(Y_test, Y_pred)
    precision = precision_score(Y_test, Y_pred, average='macro', zero_division=0)
    recall = recall_score(Y_test, Y_pred, average='macro', zero_division=0)
    f1 = f1_score(Y_test, Y_pred, average='macro', zero_division=0)
    
    # Mostrar resultados
    print(f"=== Resultados para k = {k} ===")
    print(f"Accuracy:    {accuracy:.4f}")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"F1-Score:    {f1:.4f}\n")