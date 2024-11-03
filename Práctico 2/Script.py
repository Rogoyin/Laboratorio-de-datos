'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    Archivo principal para ejecutar paso por paso todas las etapas del trabajo práctico.

    Prerrequisito:
        Contar con el dataset TMNIST en formato CSV en la misma ubicación que el actual archivo
    
    El presente script se divide en las siguientes etapas:
        1. Carga del dataset TMNIST
        2. Generación de gráficos relevantes
        3. Clasificación binaria: generación de modelo de KNN
        4. Clasificación multiclase: generación de modelo de árbol de decisión

'''

from Auxiliares.Graficos import graficar
from Auxiliares.ClasificacionBinaria import clasificacion_binaria
from Auxiliares.ClasificacionMulticlase import clasificacion_multiclase
import pandas as pd

# Carga del dataset TMNIST
df_digitos = pd.read_csv('TMNIST_Data.csv')

# Generar todas las visualizaciones
graficar(df_digitos, 'Graficos/')

# Análisis, entrenamiento y testeo relativos al Ejercicio 2 (Clasificación Binaria)
clasificacion_binaria()

# Análisis, entrenamiento y testeo relativos al Ejercicio 3 (Clasificación Multiclase)
clasificacion_multiclase()







