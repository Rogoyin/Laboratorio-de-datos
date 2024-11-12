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
import matplotlib.pyplot as plt

'''
    FUNCIONES AUXILIARES
'''
def aplanar(x: int, y: int):
    # Función para convertir una coordenada (x, y) con x, y entre [0, 27] a un digito entre 1 y 784
    # Esto sirve para convertir fácilmente una coordenada a una columna del dataset de dígitos
    return (x*28) + y + 1


def clasificar_tres_atributos(train: pd.DataFrame, test: pd.DataFrame):
    # Se elijen distintas tuplas (x_1, y_1, x_2, y_2, x_3, y_3) para seleccionar los atributos correspondientes (esto se explica en el informe, Sección 4.1)
    t1 = (10, 9, 15, 19, 21, 22)
    t2 = (8, 16, 15, 25, 22, 14)
    t3 = (15, 3, 15, 11, 22, 11)
    tuplas = [t1, t2, t3]

    # Una lista de valores X que serán dataframes train (habrá uno por cada tupla)
    X_list = [] 
    for t in tuplas:
        # Se utiliza la tupla t para generar el dataframe train "X_t"
        X_list.append(train[[str(aplanar(t[0], t[1])), str(aplanar(t[2], t[3])), str(aplanar(t[4], t[5]))]])

    # El atributo de testeo será igual para todos los train
    Y = train['labels']

    # Creación y entrenamiento de los modelos KNN (con K = 5, por tener que elegir un valor)
    k = 5
    models = []
    for X in X_list:
        # Además de crearlos, se los entrena ya con su correspondiente X (de X_list)
        models.append(KNeighborsClassifier(n_neighbors = k).fit(X, Y))


    # Una lista de valores X_test, que serán el subconjunto de test correspondiente a cada tupla
    X_test_list = []
    for t in tuplas:
        # Se utiliza la tupla t para generar el dataframe train "X_t"
        X_test_list.append(test[[str(aplanar(t[0], t[1])), str(aplanar(t[2], t[3])), str(aplanar(t[4], t[5]))]])

    # El atributo de testeo será igual para todos los X_test
    Y_test = test['labels']

    # Realizar predicciones por cada modelo y agregarlas en orden en Y_predict_list
    Y_predict_list = []
    for i in range(0, len(models)):
        Y_predict_list.append(models[i].predict(X_test_list[i]))

    # Chequear la exactitud (accuracy) de cada conjunto de predicciones
    scores = []
    for Y_predict in Y_predict_list:
        scores.append(metrics.accuracy_score(Y_test, Y_predict))

    # Imprimir los valores de exactitud para cada modelo
    print("Resultados ejercicio 2.C parte 1: exactitud de tres modelos correspondientes a tres tuplas particulares")
    for i in range(0, len(scores)):
        print("Exactitud del modelo", str(i), ":", str(scores[i]))


def clasificar_variando_atributos(train: pd.DataFrame, test: pd.DataFrame, ruta_graficos: str):
    # Se varía entre una y diez coordenadas, elegidas "aleatoriamente" y se mide la exactitud para cada cantidad de atributos (coordenadas) a utilizar
    coordenadas = [(8, 16), (15, 25), (22,14), (20, 20), (15, 6), (20, 23), (15, 15), (20, 6), (10, 9), (25, 15)]

    # Aplicar a cada coordenada la función aplanar, para obtener los atributos exactos a utilizar en el dataframe
    # Esto resultará en ['241', '446', '631', '436', '427', '584', '290', '567', '716', '424']
    atributos = [str(aplanar(c1, c2)) for (c1, c2) in coordenadas]

    # Se generarán diez modelos a entrenar, cada uno agregando un nuevo atributo respecto del modelo anterior
    # Es decir, resultará en una lista [['241'], ['241', '446'], ['241', '446', '631'], ...]
    atributos_acum = []
    for i in range(0, len(atributos)):
        atributos_acum.append(atributos[0:(i+1)])

    # Una lista de valores X que serán dataframes train (habrá uno por cada tupla)
    X_list = [] 
    for attrs in atributos_acum:
        # Se utilizan los atributos a_1, a_2, ..., a_i para generar el dataframe train "X_i"
        X_list.append(train[attrs])

    # El atributo de testeo será igual para todos los train
    Y = train['labels']

    # Creación y entrenamiento de los modelos KNN (con K = 5, por tener que elegir un valor)
    k = 5
    models = []
    for X in X_list:
        # Además de crearlos, se los entrena ya con su correspondiente X (de X_list)
        models.append(KNeighborsClassifier(n_neighbors = k).fit(X, Y))


    # Una lista de valores X_test, que serán el subconjunto de test correspondiente a cada tupla
    X_test_list = []
    for attrs in atributos_acum:
        # Se utilizan los atributos a_1, a_2, ..., a_i para generar el dataframe test "X_test_i"
        X_test_list.append(test[attrs])

    # El atributo de testeo será igual para todos los X_test
    Y_test = test['labels']

    # Realizar predicciones por cada modelo y agregarlas en orden en Y_predict_list
    Y_predict_list = []
    for i in range(0, len(models)):
        Y_predict_list.append(models[i].predict(X_test_list[i]))

    # Chequear la exactitud (accuracy) de cada conjunto de predicciones
    scores = []
    for Y_predict in Y_predict_list:
        scores.append(metrics.accuracy_score(Y_test, Y_predict))

    # Guardar el gráfico generado
    plt.plot([1,2,3,4,5,6,7,8,9,10], scores, label='Serie de coordenadas', marker='o')
    plt.xlabel('Cantidad de atributos')
    plt.ylabel('Exactitud del modelo')
    plt.xticks(range(1,11))
    plt.legend()
    plt.grid(True)
    plt.savefig(ruta_graficos + 'Clasificacion Binaria - 2.C - Variacion de atributos.png')

    # Imprimir los valores de exactitud para cada modelo en la consola
    print("Resultados ejercicio 2.C parte 2: exactitud de diez modelos, incrementando desde 1 a 10 la cantidad de atributos")
    for i in range(0, len(scores)):
        print("Exactitud del modelo", str(i), ":", str(scores[i]))

    

    
'''
    FUNCIÓN PRINCIPAL
'''
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

    # Se clasifica eligiendo tres distintos conjuntos de tres atributos cada uno (Ejercicio 2.C, parte 1)
    clasificar_tres_atributos(train, test)

    # COMPLETAR
    clasificar_variando_atributos(train, test, ruta_graficos)


    # Además, se variarán los valores de k para poder graficar
    k_values = [1,2,3,5,8,13,21,34]

    

    # Se clasifica eligiendo tres distintos conjuntos de tres atributos cada uno y variando los valores de k (Ejercicio 2.D)
    #clasificar_variando_k(train, test, k_values, tuplas, ruta_graficos)











'''
def clasificar_variando_k(train: pd.DataFrame, test: pd.DataFrame, k: list, tuplas: list, ruta_graficos: str):


    # Se preparan los dataframes train en función de los atributos elegidos en t1, t2, t3
    # Cada tX contiene 3 coordenadas (x, y), por lo que se convierten a columnas (con aplanar(...)) y se eligen sólo las tres columnas correspondientes
    X_1 = train[[str(aplanar(t1[0], t1[1])), str(aplanar(t1[2], t1[3])), str(aplanar(t1[4], t1[5]))]]
    X_2 = train[[str(aplanar(t2[0], t2[1])), str(aplanar(t2[2], t2[3])), str(aplanar(t2[4], t2[5]))]]
    X_3 = train[[str(aplanar(t3[0], t3[1])), str(aplanar(t3[2], t3[3])), str(aplanar(t3[4], t3[5]))]]

    # El atributo de testeo será igual para todos los train
    Y = train['labels']

    # Creación de los modelos KNN (con K = 5)
    modelo_1 = KNeighborsClassifier(n_neighbors = k)
    modelo_2 = KNeighborsClassifier(n_neighbors = k)
    modelo_3 = KNeighborsClassifier(n_neighbors = k)

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

    #Scores
    a1 = metrics.accuracy_score(Y_test, Y_1_pred)
    a2 = metrics.accuracy_score(Y_test, Y_2_pred)
    a3 = metrics.accuracy_score(Y_test, Y_3_pred)

    # Chequear métrica de exactitud
    print("Exactitud del modelo 1:", a1)
    print("Exactitud del modelo 2:", a2)
    print("Exactitud del modelo 3:", a3)

    pass
'''