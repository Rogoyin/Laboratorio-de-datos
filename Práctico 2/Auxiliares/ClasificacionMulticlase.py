'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    Este programa describe funciones para realizar una clasificación multiclase de dígitos manuscritos utilizando un modelo de árbol de decisión. Estas funciones
    describen las siguientes tareas:
        1. Preparación de los datos, dividiéndolos en datos de desarrollo y held-out.
        2. Entrenamiento de modelos con profundidades de 1 a 10, calculando su precisión en el conjunto de desarrollo.
        3. Validación cruzada.
        4. Evaluación final entrenando el modelo óptimo utilizando los datos de desarrollo completos y evalúa su desempeño en el conjunto de validación, 
        generando métricas finales de precisión, informe de clasificación y una matriz de confusión visualizada con un mapa de calor.

"""

'''

# %% Importación de paquetes necesarios.
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# %% Funciones.

def entrenar_arbol_decision(x_entrenamiento: pd.DataFrame, y_entrenamiento: pd.Series, profundidad_maxima: int) -> DecisionTreeClassifier:

    """
    Entrenar un clasificador de árbol de decisión con una profundidad máxima dada.
    
    Parámetros:
        x_entrenamiento (pd.DataFrame): Conjunto de características de entrenamiento.
        y_entrenamiento (pd.Series): Conjunto de etiquetas de entrenamiento.
        profundidad_maxima (int): Profundidad máxima del árbol de decisión.
    
    Retorna:
        DecisionTreeClassifier: El modelo entrenado.

    """

    modelo = DecisionTreeClassifier(max_depth=profundidad_maxima, random_state=42)
    modelo.fit(x_entrenamiento, y_entrenamiento)
    return modelo

def evaluar_con_validacion_cruzada(x_entrenamiento: pd.DataFrame, y_entrenamiento: pd.Series, rango_profundidades: range, ruta_guardado: str = None) -> dict:

    """
    Evaluar árboles de decisión con diferentes profundidades utilizando validación cruzada k-fold.
    
    Parámetros:
        x_entrenamiento (pd.DataFrame): Conjunto de características de entrenamiento.
        y_entrenamiento (pd.Series): Conjunto de etiquetas de entrenamiento.
        rango_profundidades (range): Rango de valores de profundidad máxima a evaluar.
    
    Retorna:
        dict: Diccionario con la mejor profundidad y su puntuación correspondiente.
    """

    mejor_puntuacion = 0
    mejor_profundidad = None
    puntuaciones_promedio = []  # Lista para almacenar las puntuaciones promedio de cada profundidad.

    for profundidad in rango_profundidades:
        modelo = DecisionTreeClassifier(max_depth=profundidad, random_state=42)
        puntuaciones = cross_val_score(modelo, x_entrenamiento, y_entrenamiento, cv=5, scoring='accuracy')  # Validación cruzada k-fold de 5.
        puntuacion_promedio = np.mean(puntuaciones)
        
        puntuaciones_promedio.append(puntuacion_promedio)
        
        if puntuacion_promedio > mejor_puntuacion:
            mejor_puntuacion = puntuacion_promedio
            mejor_profundidad = profundidad
    
    # Graficar las puntuaciones de las diferentes profundidades.
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=list(rango_profundidades), y=puntuaciones_promedio, marker='o', color='b', label='Precisión Promedio')
    plt.xlabel('Profundidad del árbol', fontsize=12)
    plt.ylabel('Precisión promedio', fontsize=12)
    plt.grid(True)
    plt.xticks(rango_profundidades)

    # Guardar o mostrar el gráfico.
    if ruta_guardado:
        plt.savefig(ruta_guardado + 'Exactitudes_Arboles', bbox_inches='tight')  # Guarda la imagen en la ruta especificada.
    else:
        plt.show()

    return {'mejor_profundidad': mejor_profundidad, 'mejor_puntuacion': mejor_puntuacion}

def evaluar_modelo_conjunto_validacion(x_entrenamiento: pd.DataFrame, y_entrenamiento: pd.Series, 
                                       x_prueba: pd.DataFrame, y_prueba: pd.Series, 
                                       mejor_profundidad: int, ruta_guardado: str = None) -> None:
    
    """
    Entrenar el mejor modelo de árbol de decisión en el conjunto completo de desarrollo 
    y evaluarlo en el conjunto de validación.

    Parámetros:
        x_entrenamiento (pd.DataFrame): Conjunto de características de desarrollo.
        y_entrenamiento (pd.Series): Conjunto de etiquetas de desarrollo.
        x_prueba (pd.DataFrame): Conjunto de características de validación.
        y_prueba (pd.Series): Conjunto de etiquetas de validación.
        mejor_profundidad (int): La mejor profundidad máxima determinada previamente.
        ruta_guardado (str, opcional): Ruta donde guardar la imagen de la matriz de confusión.
    
    """
    
    # Entrenar el modelo con la mejor profundidad.
    modelo = DecisionTreeClassifier(max_depth=mejor_profundidad, random_state=42)
    modelo.fit(x_entrenamiento, y_entrenamiento)
    
    # Realizar predicciones en el conjunto de validación.
    y_pred = modelo.predict(x_prueba)
    
    # Calcular precisión en el conjunto de validación.
    precision = accuracy_score(y_prueba, y_pred)
    print(f"Precisión en el conjunto de validación: {precision:.4f}.")
    
    # Generar informe de clasificación.
    print("\nInforme de Clasificación:")
    print(classification_report(y_prueba, y_pred))
    
    # Matriz de confusión.
    matriz_confusion = confusion_matrix(y_prueba, y_pred)
    plt.figure(figsize=(10, 7))
    sns.heatmap(matriz_confusion, annot=True, fmt="d", cmap="Blues", 
                xticklabels=range(10), yticklabels=range(10))
    plt.xlabel("Predicción")
    plt.ylabel("Verdadero")

    # Guardar o mostrar la matriz de confusión.
    if ruta_guardado:
        plt.savefig(ruta_guardado + 'Matriz_Confusion', bbox_inches='tight')  # Guarda la imagen en la ruta especificada.
    else:
        plt.show()  

# %% Carga de datos y preparación del conjunto de entrenamiento y validación.

def clasificacion_multiclase(df: pd.DataFrame, ruta_guardado: str = None):
    print('=====================================')
    print('  PUNTO 3. CLASIFICACIÓN MULTICLASE')
    print('=====================================')
    # Separar en variables explicativas (X) y variable objetivo (y).
    x = df.iloc[:, 2:].values  # Características: 784 píxeles de cada imagen.
    y = df.iloc[:, 1].values   # Etiquetas: Dígitos (clase a predecir).

    # Dividir los datos en conjunto de desarrollo (entrenamiento) y de validación (held-out).
    x_desarrollo, x_validacion, y_desarrollo, y_validacion = train_test_split(x, y, test_size=0.2, random_state=42)

    # %% Entrenamiento de modelos de árboles de decisión con distintas profundidades.

    profundidades = range(1, 11)  # Profundidades de 1 a 10.
    precisiones = []

    for profundidad in profundidades:
        modelo = entrenar_arbol_decision(x_desarrollo, y_desarrollo, profundidad)
        y_pred = modelo.predict(x_desarrollo)
        precision = accuracy_score(y_desarrollo, y_pred)
        precisiones.append(precision)

    # Identificar la mejor profundidad según la precisión.
    mejor_profundidad = profundidades[precisiones.index(max(precisiones))]
    print(f"Mejor profundidad: {mejor_profundidad} con precisión: {max(precisiones):.4f}.")

    # %% Validación cruzada para seleccionar el mejor modelo.

    # Realizar validación cruzada en el conjunto de desarrollo.
    resultado_cv = evaluar_con_validacion_cruzada(x_desarrollo, y_desarrollo, range(1, 11), ruta_guardado = ruta_guardado)
    print(f"Mejor profundidad según validación cruzada: {resultado_cv['mejor_profundidad']} con precisión CV: {resultado_cv['mejor_puntuacion']:.4f}.")

    # %% Evaluación del mejor modelo en el conjunto de validación.

    # Entrenar el mejor modelo en el conjunto de desarrollo y evaluarlo en el conjunto de validación.
    evaluar_modelo_conjunto_validacion(x_desarrollo, y_desarrollo, x_validacion, y_validacion, resultado_cv['mejor_profundidad'], ruta_guardado = ruta_guardado)
