'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    Archivo encargado de generar gráficos utilizando el dataset de dígitos. 

    Prerrequisito:
        Contar con el dataset TMNIST en formato CSV
    
    Modo de uso:
        Importar el archivo actual y llamar a la función graficar(...), pasando como parámetros:
            - ruta_origen, carpeta en donde se ubicará el dataset (i.e. '../')
            - archivo_csv, nombre del archivo CSV que contiene el dataset (i.e. 'TMNIST_Data.csv')
            - ruta_destino, carpeta en donde se almacenarán los gráficos (i.e. '../Graficos/')

'''

# Importar bibliotecas necesarias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Función principal que será llamada al importar el archivo desde otro archivo
def graficar(ruta_origen: str, archivo_csv: str, ruta_destino: str):
    df_digitos = cargar_archivo(ruta_origen + archivo_csv)

    generar_heatmaps_variaciones(df_digitos, ruta_destino)





def cargar_archivo(ruta: str):
    return pd.read_csv(ruta)

# %% # Gráficos de heatmap para análisis inicial del dataset
def generar_heatmaps_variaciones(df_digitos: pd.DataFrame, ruta_destino: str):
    columnas = df_digitos.columns
    columnas = columnas[2:] # Remover las columnas 'names' y 'labels'

    # Matriz para analizar pixel a pixel (columna a columna) el dataset completo
    matriz_variabilidad_global = [[-1]*28 for z in range(28)]

    # Filtrar por cada dígito entre 0 y 9 y generar su gráfico
    for digito in df_digitos['labels'].unique():
        df_digito_actual = df_digitos[df_digitos['labels'] == digito]
    
        # La matriz comienza con ceros y almacenará la cantidad de valores únicos de la escala de grises de entre las imágenes del dígito actual
        matriz_variabilidad_clase = [[0]*28 for z in range(28)]
        
        for col in columnas:
            x, y = 0, 0
            col_num = int(col)
            
            if col_num <= 28:
                x = col_num - 1
                y = 0
            elif col_num < 784:
                x = col_num % 28
                y = col_num // 28
            else:
                x, y = 27, 27
        
            matriz_variabilidad_clase[y][x] = len(df_digito_actual[col].unique())   # Almacenar variabilidad de clase (dígito) actual
            
            if (matriz_variabilidad_global[y][x] == -1):
                matriz_variabilidad_global[y][x] = len(df_digitos[col].unique())    # Almacenar variabilidad tomando todas las clases (dígitos)
        
        # Cambiar a tipo np.array para ser graficado
        matriz_variabilidad_clase = np.array(matriz_variabilidad_clase)
        
        # Crear el heatmap
        plt.figure(figsize=(8, 8))
        plt.imshow(matriz_variabilidad_clase, cmap='hot', interpolation='nearest', vmin=1, vmax=256)
        plt.colorbar(label='Cantidad de valores únicos')
        plt.title('Distribución de valores únicos en imágenes de 28x28 - Dígito ' + str(digito))
        plt.xlabel('Eje X')
        plt.ylabel('Eje Y')
        plt.savefig(ruta_destino + 'Distribucion Digito ' + str(digito) + '.png')

    # Cambiar a tipo np.array para ser graficado
    matriz_variabilidad_global = np.array(matriz_variabilidad_global)
    
    # Crear el heatmap
    plt.figure(figsize=(8, 8))
    plt.imshow(matriz_variabilidad_global, cmap='hot', interpolation='nearest', vmin=1, vmax=256)
    plt.colorbar(label='Cantidad de valores únicos')
    plt.title('Distribución de cantidad de valores únicos en imágenes de 28x28')
    plt.xlabel('Eje X')
    plt.ylabel('Eje Y')
    #plt.show()
    plt.savefig(ruta_destino + 'Distribucion general de digitos.png')
