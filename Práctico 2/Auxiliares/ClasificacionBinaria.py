'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    El método principal, clasificacion_binaria(), se divide en las siguientes etapas:
        1. Construcción de un nuevo dataframe que contenga sólo los dígitos 0 y 1
        2. Separar los datos en conjuntos de train y test
'''

import pandas as pd

def clasificacion_binaria(df_digitos: pd.DataFrame, ruta_graficos: str):
    # %% ETAPA 1: Construccion de un nuevo dataframe sólo con dígitos 0 y 1 y balanceo
    df_ceros_unos = df_digitos[(df_digitos['labels'] == 0) | (df_digitos['labels'] == 1)].copy().reset_index(drop=True)

    # Chequeo del subconjunto anterior sobre balanceo de clases en la muestra
    df_ceros = df_ceros_unos[(df_ceros_unos['labels'] == 0)]
    df_unos = df_ceros_unos[(df_ceros_unos['labels'] == 1)]

    assert df_ceros.shape[0] == df_unos.shape[0], "Error: hay distinta cantidad de ceros y unos en el subconjunto df_ceros_unos"
    assert df_ceros.groupby('names')['names'].count().equals(df_unos.groupby('names')['names'].count()), "Error"

    # %% ETAPA 2: Separar los datos en conjuntos de train y test
    