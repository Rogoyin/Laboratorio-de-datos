'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    El método principal, clasificacion_binaria(), se divide en las siguientes etapas:
        1. Construcción de un nuevo dataframe que contenga sólo los dígitos 0 y 1
        2. Separar los datos en conjuntos de train y test
'''

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
import pandas as pd

def aplanar(x: int, y: int):
    # Función para convertir una coordenada (x, y) con x, y entre [0, 27] a un digito entre 1 y 784
    # Esto sirve para convertir fácilmente una coordenada a una columna del dataset de dígitos
    return (x*28) + y + 1

def clasificacion_binaria(df_digitos: pd.DataFrame, ruta_graficos: str):
    # %% ETAPA 1: Construccion de un nuevo dataframe sólo con dígitos 0 y 1 y balanceo
    df_ceros_unos = df_digitos[(df_digitos['labels'] == 0) | (df_digitos['labels'] == 1)].copy()

    # Chequeo del subconjunto anterior sobre balanceo de clases en la muestra
    df_ceros = df_ceros_unos[(df_ceros_unos['labels'] == 0)]
    df_unos = df_ceros_unos[(df_ceros_unos['labels'] == 1)]

    assert df_ceros.shape[0] == df_unos.shape[0], "Error: hay distinta cantidad de ceros y unos en el subconjunto df_ceros_unos"
    assert df_ceros.groupby('names')['names'].count().equals(df_unos.groupby('names')['names'].count()), "Error"

    # %% ETAPA 2: Separar los datos en conjuntos de train y test
    
    # Se realiza una partición aleatoria (aunque con una semilla/seed definida, para poder reproducir el mismo resultado en distintas ejecuciones)
    # El 80% será destinado a train y 20% a test
    train_ceros, test_ceros = train_test_split(df_ceros, test_size=0.2, random_state=42)
    train_unos, test_unos = train_test_split(df_unos, test_size=0.2, random_state=42)

    train = pd.concat([train_ceros, train_unos], ignore_index=True, sort=False)
    test = pd.concat([test_ceros, test_unos], ignore_index=True, sort=False)

    # %% ETAPA 3: Ajustar un modelo de KNN considerando distintas triplas de atributos
    
    # Se elijen distintas tuplas (x_1, y_1, x_2, y_2, x_3, y_3) para seleccionar los atributos correspondientes
    t1 = (0, 0, 13, 13, 27, 27)
    t2 = (13, 0, 13, 13, 13, 27)
    t3 = (13, 10, 13, 13, 13, 16)

    # Se preparan los dataframes train en función de los atributos elegidos en t1, t2, t3
    # Cada tX contiene 3 coordenadas (x, y), por lo que se convierten a columnas (con aplanar(...)) y se eligen sólo las tres columnas correspondientes
    X_1 = train[[str(aplanar(t1[0], t1[1])), str(aplanar(t1[2], t1[3])), str(aplanar(t1[4], t1[5]))]]
    X_2 = train[[str(aplanar(t2[0], t2[1])), str(aplanar(t2[2], t2[3])), str(aplanar(t2[4], t2[5]))]]
    X_3 = train[[str(aplanar(t3[0], t3[1])), str(aplanar(t3[2], t3[3])), str(aplanar(t3[4], t3[5]))]]

    # El atributo de testeo será igual para todos los train
    Y = train['labels']

    # Creación de los modelos KNN (con K = 5)
    modelo_1 = KNeighborsClassifier(n_neighbors = 5)
    modelo_2 = KNeighborsClassifier(n_neighbors = 5)
    modelo_3 = KNeighborsClassifier(n_neighbors = 5)

    # Entrenar los modelos
    modelo_1.fit(X_1, Y)
    modelo_2.fit(X_2, Y)
    modelo_3.fit(X_3, Y)

    # Preparar los datos X_test para generar predicciones
    X_1_test = test[[str(aplanar(t1[0], t1[1])), str(aplanar(t1[2], t1[3])), str(aplanar(t1[4], t1[5]))]]
    X_2_test = test[[str(aplanar(t2[0], t2[1])), str(aplanar(t2[2], t2[3])), str(aplanar(t2[4], t2[5]))]]
    X_3_test = test[[str(aplanar(t3[0], t3[1])), str(aplanar(t3[2], t3[3])), str(aplanar(t3[4], t3[5]))]]

    # El atributo de testeo será igual para todos los X_test
    Y_test = test['labels']

    # Realizar predicciones
    Y_1_pred = modelo_1.predict(X_1_test)
    Y_2_pred = modelo_2.predict(X_2_test)
    Y_3_pred = modelo_3.predict(X_3_test)

    # Chequear métrica de exactitud
    print("Exactitud del modelo 1:", metrics.accuracy_score(Y_test, Y_1_pred))
    print("Exactitud del modelo 2:", metrics.accuracy_score(Y_test, Y_2_pred))
    print("Exactitud del modelo 3:", metrics.accuracy_score(Y_test, Y_3_pred))


