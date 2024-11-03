'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    Archivo encargado de generar gráficos utilizando el dataset de dígitos. 
    El método principal es graficar(...)

    Prerrequisito:
        Se debe recibir como parámetro el dataset TMNIST como DataFrame
    
    Modo de uso:
        Importar el archivo actual y llamar a la función graficar(...), pasando como parámetros:
            - df_digitos, dataframe del dataset TMNIST
            - ruta_destino, carpeta en donde se almacenarán los gráficos (i.e. '../Graficos/')

'''

# Importar bibliotecas necesarias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Función principal que será llamada al importar el archivo desde otro archivo
def graficar(df_digitos: pd.DataFrame, ruta_destino: str):

    # Graficos para ejercicio 1.A (usados en Sección 2.2 y 2.3)
    generar_heatmaps_variaciones(df_digitos, ruta_destino)

    # Graficos para ejercicio 1.B (usados en Sección 2.4)
    generar_heatmaps_diferencias(df_digitos, ruta_destino, 1, 3)
    generar_heatmaps_diferencias(df_digitos, ruta_destino, 3, 8)
    generar_heatmaps_diferencias(df_digitos, ruta_destino, 0, 1)

    # Generacion de las 29.900 imágenes (OJO, demora ~2 min) 
        # generar_imagenes_raw(df_digitos, ruta_destino + 'Raw/')



'''
    Funciones auxiliares
'''

# %% # Gráficos de heatmap para análisis inicial del dataset e importancia de atributos
def generar_heatmaps_variaciones(df_digitos: pd.DataFrame, ruta_destino: str):
    columnas = df_digitos.columns
    columnas = columnas[2:] # Remover las columnas 'names' y 'labels'

    # Matriz para analizar pixel a pixel (columna a columna) el dataset completo
    # Se llena de -1 para tener una noción de si ya fue actualizada o no cada celda
    matriz_variabilidad_global = [[-1]*28 for z in range(28)]

    # Filtrar por cada dígito entre 0 y 9 y generar su gráfico
    for digito in df_digitos['labels'].unique():
        df_digito_actual = df_digitos[df_digitos['labels'] == digito]
    
        # La matriz de 28x28 comienza con ceros y almacenará la cantidad de valores únicos de la escala de grises de entre las imágenes del dígito actual
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
        
            # Almacenar la cantidad de valores únicos de intensidad del pixel (x,y) en la escala de grises
            matriz_variabilidad_clase[y][x] = len(df_digito_actual[col].unique())
            
            # Para el pixel (x,y) almacenar variabilidad, pero esta vez tomando todas las clases/dígitos 
            if (matriz_variabilidad_global[y][x] == -1):
                matriz_variabilidad_global[y][x] = len(df_digitos[col].unique())
        
        # Cambiar a tipo np.array para ser graficado
        matriz_variabilidad_clase = np.array(matriz_variabilidad_clase)
        
        # Crear el heatmap
        # plt.title('Distribución de valores únicos en imágenes de 28x28 - Dígito ' + str(digito))
        plt.figure(figsize=(8, 8))
        plt.imshow(matriz_variabilidad_clase, cmap='hot', interpolation='nearest', vmin=1, vmax=256)
        plt.colorbar(label='Cantidad de valores únicos')
        plt.xlabel('Eje X')
        plt.ylabel('Eje Y')
        plt.savefig(ruta_destino + 'Distribucion Digito ' + str(digito) + '.png')

    # Cambiar a tipo np.array para ser graficado
    matriz_variabilidad_global = np.array(matriz_variabilidad_global)
    
    # Crear el heatmap
    # plt.title('Distribución de cantidad de valores únicos en imágenes de 28x28')
    plt.figure(figsize=(8, 8))
    plt.imshow(matriz_variabilidad_global, cmap='hot', interpolation='nearest', vmin=1, vmax=256)
    plt.colorbar(label='Cantidad de valores únicos')
    plt.xlabel('Eje X')
    plt.ylabel('Eje Y')
    #plt.show()
    plt.savefig(ruta_destino + 'Distribucion general de digitos.png')


    # %% # Gráficos de heatmap para análisis de diferencias entre dígitos (diferencia pixel a pixel, diferencia simétrica de valores de intensidad únicos)
def generar_heatmaps_diferencias(df_digitos: pd.DataFrame, ruta_destino: str, digito1: int, digito2: int):
    columnas = df_digitos.columns

    # Remover las columnas 'names' y 'labels' para que sólo queden las referentes a coordenadas de la imagen (ordenadas)
    columnas = columnas[2:]

    df_digito_1 = df_digitos[df_digitos['labels'] == digito1]
    df_digito_2 = df_digitos[df_digitos['labels'] == digito2]
    
    # La matriz de 28x28 comienza con ceros
    matriz_variabilidad_diferencias = [[0]*28 for z in range(28)]
    
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

        # Almacenar la diferencia simétrica de valores únicos de intensidad del pixel (x,y) en escala de grises
        matriz_variabilidad_diferencias[y][x] = len(set(df_digito_1[col].unique()).symmetric_difference(set(df_digito_2[col].unique())))
        
    # Cambiar a tipo np.array para graficar
    matriz_variabilidad_diferencias = np.array(matriz_variabilidad_diferencias)
    
    # Crear el heatmap
    # plt.title('Diferencia simétrica entre valores únicos de pixeles entre digitos ' + str(digito1) + ' y ' + str(digito2))
    plt.figure(figsize=(8, 8))
    plt.imshow(matriz_variabilidad_diferencias, cmap='hot', interpolation='nearest', vmin=1, vmax=256)
    plt.colorbar(label='Cantidad de valores únicos')
    plt.xlabel('Eje X')
    plt.ylabel('Eje Y')
    plt.savefig(ruta_destino + 'Diferencia simetrica entre ' + str(digito1) + ' y ' + str(digito2) + '.png')
    

# %% # Gráficos de heatmap de promedio de diferencias entre dígitos
def generar_heatmaps_promedio_diferencias(df_digitos: pd.DataFrame, ruta_destino: str):
    # TODO
    pass





# %% # Generacion de todas las imagenes en formato PNG
def generar_imagenes_raw(df_digitos: pd.DataFrame, ruta_destino: str):
    ancho_img = 28
    alto_img = 28

    # Para cada registro del dataset (de las 29.900 totales)
    for i in range(0, df_digitos.shape[0]):
        registro = df_digitos.iloc[[i]]                         # Tomar el i-ésimo registro
        fuente = registro.names.values[0]                       # Obtener la fuente con la que se dibujó
        digito = registro.labels.values[0]                      # El dígito que representa la imagen
        pixels = registro[registro.columns[-784:]].to_numpy()   # Las restantes 784 columnas, en forma de np.array, cada una representando un pixel
        
        # La imagen será en escala de grises (por eso el 'L')
        img = Image.new('L', (ancho_img, alto_img))
        img_matrix = img.load()
        for y in range(0, ancho_img):
            for x in range(0, alto_img):
                # Asignamos la columna (y*28 + x)-ésima al pixel (x,y)
                img_matrix[x, y] = int(pixels[0][y*28 + x])

        # Agrandar la imagen (de lo contrario sería difícil ver una imagen de 28x28) y guardarla
        img = img.resize((ancho_img * 10, alto_img * 10), resample=Image.NEAREST)
        img.save(ruta_destino + fuente + ' - Digito ' + str(digito) + '.png')


########################
###### DEPRECATE #######
########################

    '''
    Hay veces que es bueno mezclar (para Kfold) al azar y a veces no, depende del problema
        Hay veces que es malo: los datos tenían correlación entre las muestras (serie de tiempo -- mezclar rompe la estructura)
        A veces la meustra tiene otras correlaciones y es malo mezclar:
            Datos de audio (personas hablando) , identificar las personas
                Si el entrenamiento es con datos que uso tanto en training como en test, entonces no sabe predecir escenarios reales
                Si tengo 5 audios de A, B, C y D, DEBO usar todos los de A o bien en test o en training, no ponerlo en ambos... 
                    sino no aprende a detectar ladrones por ejemplo con voces nuevas


                    SKLEARN -- STRATIFY (es para hacer cross con K-fold en python)
    '''
