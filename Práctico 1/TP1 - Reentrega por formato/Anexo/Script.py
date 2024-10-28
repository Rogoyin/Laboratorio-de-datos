'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    El presente Script se divide en las siguientes etapas:
        1 - Generación automática de tablas descritas en nuestro modelo basado en los datasets de migraciones, sedes y secciones
        2 - Ejecución de los 4 ejercicios de SQL y sus reportes resultantes
        3 - Generación de gráficos en base a los puntos anteriores
'''

# Bibliotecas necesarias para manejo de dataframes y consultas SQL (ETAPAS 1 y 2)
import pandas as pd
import sqlite3
from pandasql import sqldf

# Bibliotecas necesarias para visualización y generación de gráficos (ETAPA 3)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns


# %% # ETAPA 1 - Generación automática de tablas descritas en nuestro modelo basado en los datasets de migraciones, sedes y secciones

'''
    1 - Generación automática de tablas descritas en nuestro modelo basado en los datasets de migraciones, sedes y secciones
    
    Prerrequisitos:
        Los archivos necesarios descritos en el enunciado del Trabajo Práctico estarán ubicados dentro de la carpeta TablasOriginales/
            - datos_migraciones.csv
            - lista-sedes-datos.csv*
            - lista-secciones.csv
        *) Es importante antes de usar el script corregir la linea 16 de lista-sedes-datos.csv, usando un editor de texto:
            Remover el "", justo antes de "VII  Región  del  Maule;  VIII  Región  del  Bio  Bio;  IX  Region  de  la  Araucania;  XVI  Region  de  Ñuble"
            No aplicar este paso genera un error en pandas al leer el archivo, dado que el registro 15 se leería como si tuviera una columna más de las determinadas
        **) El archivo lista-sedes.csv no será utilizado, como se explica en el informe, porque lista-sedes-datos.csv lo incluye en los valores que se consideran relevantes

    Descripción:
        El script toma los archivos provistos y en base a ellos crea nuevas tablas basadas en el modelo DER que especificamos en el informe.
        Las etapas son:
            1) Creación de tabla Migrantes.csv (basado en datos_migraciones.csv)
            2) Creación de tabla Regiones.csv (basado en lista-sedes-datos.csv)
            3) Creación de tabla Paises.csv (basado en datos_migraciones.csv y lista-sedes-datos.csv)
            4) Creación de tabla Redes_Sociales.csv (basado en lista-sedes-datos.csv)
            5) Creación de tabla Sedes.csv (basado en lista-sedes-datos.csv)
            6) Creación de tabla Secciones.csv (basado en lista-secciones.csv)

    Ejecución:
        Ejecutar este módulo genera las tablas en la carpeta ./TablasLimpias/
'''

# Carga de datasets
Ruta = 'TablasOriginales/'
Dataset_Migraciones = 'datos_migraciones.csv'
Dataset_Sedes = 'lista-sedes-datos.csv'
Dataset_Secciones = 'lista-secciones.csv'

# Creación de dataframes para uso posterior
Migraciones_DB = pd.read_csv(Ruta + Dataset_Migraciones)
Sedes_DB = pd.read_csv(Ruta + Dataset_Sedes)
Secciones_DB = pd.read_csv(Ruta + Dataset_Secciones)


'''
    Etapa 1: Creación de la tabla Migrantes
'''

# Comenzamos el filtrado. Notamos que los registros son redundantes respecto del atributo 'Migration by Gender Code'.
# Los valores enumerados 'FEM', 'MAL' y 'TOT' representan migraciones de mujeres, hombres y la suma de ambas, respectivamente.
# Sólo nos quedaremos con los 'TOT' dado que esta distinción es innecesaria a los fines del objetivo de estudio.
Migrantes = Migraciones_DB[Migraciones_DB['Migration by Gender Code'] == 'TOT']

# Removemos las filas pertenecientes a "Refugiados", ya que no es un país.
Migrantes = Migrantes[~(Migrantes['Country Origin Name'] == 'Refugees')]

# Nos quedamos sólo con los registros que incluyen a Argentina como el origen o el destino de una migración.
Migrantes = Migrantes[(Migrantes['Country Origin Code'] == 'ARG') | (Migrantes['Country Dest Code'] == 'ARG')]

# Filtramos las columnas a las que nos importan. Además, reseteamos el índice para no generar problemas.
Columnas = ['Country Origin Code', 'Country Dest Code', '1960 [1960]', '1970 [1970]', '1980 [1980]', '1990 [1990]', '2000 [2000]']

Migrantes = Migrantes[Columnas]
Migrantes = Migrantes.reset_index(drop=True)

# Verificamos que los países de Origen sean los mismos que los de destino. Sólo 'Refugees' no coincidía, pero lo removimos en pasos anteriores.
Origen = sorted(list(Migrantes['Country Origin Code'].unique()))
Destino = sorted(list(Migrantes['Country Dest Code'].unique()))

assert Origen == Destino, "Error: los países de Origen y Destino contienen alguna diferencia"

# Verificamos si cada país aparece la misma cantidad de veces en cada columna
from collections import Counter

Paises_Origen = list(Migrantes['Country Origin Code'])
Paises_Destino = list(Migrantes['Country Dest Code'])

Frecuencias_Origen = Counter(Paises_Origen)
Frecuencias_Destino = Counter(Paises_Destino)

assert Frecuencias_Origen == Frecuencias_Destino, "No aparecen la misma cantidad de veces los países."

# Cambiamos los nombres de los atributos para que no haya espacios y sea más legible
Nuevos_Nombres = {'Country Origin Code': 'id_pais_origen',
                  'Country Dest Code': 'id_pais_destino',
                  '1960 [1960]': 'cantidad_en_1960',
                  '1970 [1970]': 'cantidad_en_1970',
                  '1980 [1980]': 'cantidad_en_1980',
                  '1990 [1990]': 'cantidad_en_1990',
                  '2000 [2000]': 'cantidad_en_2000'}

Migrantes = Migrantes.rename(columns=Nuevos_Nombres)

# En todas las columnas con cantidades de migrantes debe haber enteros, por lo que si hay strings, los convertimos en NULL (hay varios valores '..')
Columnas_Numericas = ['cantidad_en_1960', 'cantidad_en_1970', 'cantidad_en_1980', 
                      'cantidad_en_1990', 'cantidad_en_2000']

for Columna in Columnas_Numericas:
    Migrantes[Columna] = pd.to_numeric(Migrantes[Columna], errors='coerce')

# Reemplazamos los NULLS con 0. Esto es porque en la tabla había "." para cuando no había habido migraciones en ninguna de las columnas numéricas, por lo que 0 es un relleno correcto.
for Columna in Columnas_Numericas:
    Migrantes[Columna] = Migrantes[Columna].fillna(0)

# Por si acaso, borramos espacios entre palabras al principio y al final
Columnas_String = ['id_pais_origen', 'id_pais_destino']

for Columna in Columnas_String:
    Migrantes[Columna] = Migrantes[Columna].str.strip().str.replace(r'\s+', ' ', regex=True)

# Hay una fila que tiene a ARG de los dos lados: la borramos
Migrantes = Migrantes[~((Migrantes['id_pais_origen'] == 'ARG') & (Migrantes['id_pais_destino'] == 'ARG'))]

# Creamos cinco DataFrames, cada uno representando dado un origen y un destino, la cantidad de migrantes en un año específico (le agregamos una columna con el año correspondiente).
# Luego, los filtramos: nos quedamos sólo con las filas con valores mayores a 0, es decir, con filas que tengan migrantes. 
# Reseteamos el índice y les cambiamos el nombre. Por último, los concatenamos en el DataFrame final.

DataFrames_Cantidades = []

for Columna in Columnas_Numericas:
    DataFrame = Migrantes[['id_pais_origen', 'id_pais_destino', Columna]].copy()    # Filtrado de columnas.
    DataFrame['anio'] = Columna[-4:len(Columna)+1]                                  # Crear columna con el año.    
    DataFrame = DataFrame.reset_index(drop=True)                                    # Resetear índices.
    DataFrame = DataFrame.rename(columns={Columna: 'migrantes'})                    # Renombrar columna.
    DataFrames_Cantidades.append(DataFrame)                                         # Agregar df a lista de dfs.

Migrantes = pd.concat(DataFrames_Cantidades).reset_index(drop=True)

# Construimos un DataFrame para los migrantes que ingresaron a la Argentina desde otro país (serán considerados Inmigrantes).
Inmigrantes = Migrantes[Migrantes['id_pais_destino'] == 'ARG'].copy()
Inmigrantes.loc[:, 'emigrantes'] = 0    # Esto sirve para el próximo paso, por ahora queda en 0 
Inmigrantes = Inmigrantes[['id_pais_origen', 'migrantes', 'emigrantes', 'anio']]
Inmigrantes = Inmigrantes.rename(columns={'id_pais_origen': 'id_pais', 'migrantes': 'inmigrantes'}).reset_index(drop=True)

# Construimos otro DataFrame para los migrantes que salieron de Argentina (serán considerados Emigrantes).
Emigrantes = Migrantes[Migrantes['id_pais_origen'] == 'ARG'].copy()
Emigrantes.loc[:, 'inmigrantes'] = 0
Emigrantes = Emigrantes[['id_pais_destino', 'inmigrantes', 'migrantes', 'anio']]
Emigrantes = Emigrantes.rename(columns={'id_pais_destino': 'id_pais', 'migrantes': 'emigrantes'}).reset_index(drop=True)

# Unimos los datos
Migrantes_ = pd.merge(
    Inmigrantes[['id_pais', 'anio', 'inmigrantes']],
    Emigrantes[['id_pais', 'anio', 'emigrantes']],
    on=['id_pais', 'anio'], 
    how='left'
).reset_index(drop=True)

Migrantes_.fillna({'inmigrantes': 0}, inplace=True)
Migrantes_.fillna({'emigrantes': 0}, inplace=True)

# Verificamos que no hay valores duplicados
Duplicados = Migrantes_[Migrantes_.duplicated(subset=['id_pais', 'anio'], keep=False)]

assert Duplicados.size == 0, "Error: con clave {id_pais, anio} existen duplicados en la tabla Migrantes"

# Guardamos la tabla en un archivo .csv
Migrantes_.to_csv('TablasLimpias/Migrantes.csv', index=False)



'''
    Etapa 2: Creación de la tabla Regiones
    
'''

# Las regiones se extraen del Dataset_Sedes
# Arreglamos discordancias de datos entre los códigos de países en Sedes y Migraciones (hay un typo en el código de Gran Bretaña)
Sedes_DB['pais_iso_3'] = Sedes_DB['pais_iso_3'].replace('GRB', 'GBR')

# Nos quedamos sólo con la columna region_geográfica, que es la que nos interesa
Regiones = pd.DataFrame(Sedes_DB['region_geografica'])

# Eliminamos espacios adicionales
Regiones['region_geografica'] = Regiones['region_geografica'].str.strip().str.replace(r'\s+', ' ', regex=True)

# Nos quedamos con valores únicos
Regiones = Regiones.drop_duplicates() 

# Ordenamos los registros alfabéticamente y reseteamos el índice para no generar problemas
Regiones = Regiones.sort_values(by='region_geografica').reset_index(drop=True)

# Generamos una nueva columna: id, con números identificatorios.
Regiones['id'] = [x for x in range(1,len(Regiones)+1)]

# Cambiamos los nombres de los atributos y ordenamos las columnas
Regiones = Regiones.rename(columns = {'region_geografica': 'nombre'})
Regiones = Regiones[['id', 'nombre']]

# Guardamos la tabla en un archivo .csv
Regiones.to_csv('TablasLimpias/Regiones.csv', index=False)



'''
    Etapa 3: Creación de la tabla Paises
'''

# Usamos los códigos y nombres de la base de datos "datos_migraciones.csv", ya que son más exhaustivos que los de las otras tablas. 
# El procedimiento para encontrar los valores únicos es:
#   1. Armar tres DataFrames: uno con los países de origen -código y nombre-, otro con los países de destino -código y nombre- 
#       y otro con los países de "Sedes". De esa forma obtenemos todos los países que están en una u otra columna pero no en las otras.
#   2. Concatenarlos verticalmente, llamando las columnas "id" (el código ISO del país) y "nombre". Este DataFrame se llamará Países.
#   3. Se eliminan las filas con valores duplicados en la columna "id".
#
# Importante: la tabla final contendrá NaNs en la clave foránea id_region. Esto fue una decisión que tomamos para permitir que los id
#   (los códigos ISO de países) sean completos pese a que en los datasets con los que trabajamos no todos los países tenían definida la región
#   geográfica. Optamos por dejarlo así en lugar de corregirlo manualmente o usar otro dataset de internet (fuera de los límites del TP, haríamos esto último).

Paises_Origen = Migraciones_DB[['Country Origin Code', 'Country Origin Name']]
Paises_Destino = Migraciones_DB[['Country Dest Code', 'Country Dest Name']]
Paises_Sedes = Sedes_DB[['pais_iso_3', 'pais_castellano']]

# Renombramos las columnas para que se llamen igual.

Nuevos_Nombres_Origen = {'Country Origin Code': 'id',
                         'Country Origin Name': 'nombre'}

Nuevos_Nombres_Destino = {'Country Dest Code': 'id',
                          'Country Dest Name': 'nombre'}

Nuevos_Nombres_Sedes = {'pais_iso_3': 'id',
                        'pais_castellano': 'nombre'}

Paises_Origen = Paises_Origen.rename(columns = Nuevos_Nombres_Origen)
Paises_Destino = Paises_Destino.rename(columns = Nuevos_Nombres_Destino)
Paises_Sedes = Paises_Sedes.rename(columns = Nuevos_Nombres_Sedes)

# Concatenamos verticalmente los dos DataFrames y creamos Paises
Paises = pd.concat([Paises_Origen, Paises_Destino, Paises_Sedes], axis=0)

# Removemos las filas pertenecientes a Refugiados, ya que no es un país
Paises = Paises[~(Paises['id'] == 'zzz')]

# Eliminamos espacios adicionales
for Columna in Paises.columns:
    Paises[Columna] = Paises[Columna].str.strip().str.replace(r'\s+', ' ', regex=True)

# Quitamos el valor NaN. Filtramos los valores repetidos de las columna "id". Además, reseteamos el índice
Paises = Paises.dropna(subset=['id'])
Paises = Paises.drop_duplicates(subset=['id']).reset_index(drop=True)

# Eliminamos los duplicados en la columna "pais_iso_3" en el DataFrame "Sedes". Esto es para que no se generen filas de más en el join
Paises_En_Sedes = Sedes_DB.drop_duplicates(subset='pais_iso_3').copy()

# Removemos espacios adicionales
for Columna in ['region_geografica', 'pais_iso_3']:
    Paises_En_Sedes[Columna] = Paises_En_Sedes[Columna].str.strip().str.replace(r'\s+', ' ', regex=True)

# Agregamos el 'id_region' correspondiente a cada país. Este se extrae del correspondiente al país en el dataset "Sedes". 
#   Si no se encuentra, queda con valor NULL

Paises = pd.merge(Paises, Paises_En_Sedes, left_on='id', right_on='pais_iso_3', how='left')[['id', 'nombre', 'region_geografica']]

# Hacemos un LEFT_JOIN con el DataFrame "Regiones" para extraer los id de las regiones correspondientes
Paises = pd.merge(Paises, Regiones, left_on='region_geografica', right_on='nombre', how='left')

# Filtramos las columnas a las que necesitamos y cambiamos nombres
Paises = Paises[['id_x', 'nombre_x', 'id_y']]
Paises = Paises.rename(columns={'id_x': 'codigo_iso', 'nombre_x': 'nombre', 'id_y': 'id_region'})

# Verificamos que no hay nulos en la columna 'id'; los removemos
Paises = Paises.dropna(subset='codigo_iso')

# Ordenamos alfabéticamente por id
Paises = Paises.sort_values(by='codigo_iso').reset_index(drop=True)

# Chequeamos que no hay duplicados en la clave primaria.
Duplicados = Paises[Paises.duplicated(subset=['codigo_iso'], keep=False)]
assert Duplicados.size == 0, "Error: con clave { codigo_iso } existen duplicados en la tabla Pais"

# Guardamos la tabla en un archivo .csv
Paises.to_csv('TablasLimpias/Paises.csv', index=False)



'''
    Etapa 4: Creación de la tabla Redes Sociales
'''

# Se extraen del dataset Sedes las redes sociales y el id de la sede a la que se vincula
SedesRedes = Sedes_DB[['sede_id', 'redes_sociales']]

Redes_Validas = []      # Guardaremos las tuplas (URL, nombre_red, id_sede) para luego cargar en un dataframe
                        #   Contendrán las redes 'Facebook', 'Twitter', 'Instagram', 'Linkedin', 'Flickr', 'Youtube'
Redes_Invalidas = []    # Guardaremos los links mal formados o @ ambiguos (IG o Twitter). No los utilizaremos pero lo hacemos por consistencia

# Dado que cada sede puede tener muchas redes sociales separadas por '  //  ', usaremos split() y guardaremos una por una 
for sede_id, redes in zip(SedesRedes['sede_id'], SedesRedes['redes_sociales']):
    # Lista con las redes sociales de esa sede (podría ser vacía)
    redes = str(redes).split('  //  ')

    for url in redes:
        # Por como son los datos, el split siempre produce un string vacío; si ese es el caso, lo pasamos por alto
        if(url == ''): continue 

        # Quitamos espacios al inicio y al final de la URL
        url = url.strip() 

        # Convertimos en minúscula la primera letra para generar mayor consistencia en los datos
        url = url[0].lower() + url[1:]

        # Si es inválida la descartamos en Redes_Invalidas, de lo contrario la guardamos junto con la compañía en Redes_Validas
        if(not url or url[0] =='@' or ' ' in url or not '.com' in url):
            Redes_Invalidas.append((url, 'Unknown', sede_id))
        else:
            if('facebook' in url): Redes_Validas.append((url, 'Facebook', sede_id))
            elif('twitter' in url): Redes_Validas.append((url, 'Twitter', sede_id))
            elif('instagram' in url): Redes_Validas.append((url, 'Instagram', sede_id))
            elif('linkedin' in url): Redes_Validas.append((url, 'Linkedin', sede_id))
            elif('flickr' in url): Redes_Validas.append((url, 'Flickr', sede_id))
            elif('youtube' in url): Redes_Validas.append((url, 'Youtube', sede_id))

# Usamos Redes_Validas para generar el dataframe
RedesSociales = pd.DataFrame(Redes_Validas, columns=['URL', 'nombre_red', 'id_sede'])

# Chequeamos que no hay duplicados en la clave primaria { URL }
Duplicados = RedesSociales[RedesSociales.duplicated(subset=['URL'], keep=False)]
assert Duplicados.size == 0, "Error: con clave { URL } existen duplicados en la tabla Redes_Sociales"

# Guardamos la tabla en un archivo .csv
RedesSociales.to_csv('TablasLimpias/Redes_Sociales.csv', index=False)



'''
    Etapa 5: Creación de la tabla Sedes
'''

# Se extraen del dataset "Sedes". Nos quedamos con las columnas que nos interesan y conforman los atributos
Sedes = Sedes_DB[['sede_id', 'sede_desc_castellano', 'pais_iso_3']]

# Cambiamos los nombres de las columnas
Sedes = Sedes.rename(columns={'sede_id': 'id_sede', 'pais_iso_3': 'codigo_iso_pais', 'sede_desc_castellano': 'nombre'})

# Borramos espacios adicionales
for Columna in Sedes.columns:
    Sedes[Columna] = Sedes[Columna].str.strip().str.replace(r'\s+', ' ', regex=True)

# Verificamos que no hay nulos en la columna 'id'; los removemos
Sedes = Sedes.dropna(subset='id_sede')

# Ordenamos alfabéticamente por id
Sedes = Sedes.sort_values(by='id_sede').reset_index(drop=True)

# Chequeamos que no hay duplicados en la clave primaria.
Duplicados = Sedes[Sedes.duplicated(subset=['id_sede'], keep=False)]
assert Duplicados.size == 0, "Error: con clave { id_sede } existen duplicados en la tabla Sedes"

# Chequeamos que todos los id_sede de la tabla Redes_Sociales están incluidos en los id_sede de Sedes
assert set(RedesSociales['id_sede'].to_list()).issubset(Sedes['id_sede'].to_list()), "Error: hay algunos id_sede en Redes_Sociales que no existen en Sedes"

# Guardamos la tabla en un archivo .csv
Sedes.to_csv('TablasLimpias/Sedes.csv', index=False)



'''
    Etapa 6: Creación de la tabla Secciones
'''
# Para armar esta tabla utilizamos el dataset "Secciones.csv"
# Importante: tomamos la decisión de que la clave primaria sea { id_sede, nombre } aunque haya habido tres casos particulares en los que
#   a igual id_sede y nombre (de sección), habían dos secciones diferentes. Entendemos que estamos restando un total de tres registros al remover 
#   duplicados y perdiendo un mínimo de información con tal que el modelo sea sólido respecto de lo que representa (no entendemos que sea necesario
#   agregar un tercer atributo en la clave principal sólo por tener que distinguir esos tres casos).

# Quitamos las columnas que no sirven y cambiamos los nombres de los atributos
Secciones = Secciones_DB[['sede_id', 'sede_desc_castellano']]
Secciones = Secciones.rename(columns={'sede_id': 'id_sede', 'sede_desc_castellano': 'nombre'})

# Borramos espacios adicionales
for Columna in Secciones.columns:
    Secciones[Columna] = Secciones[Columna].str.strip().str.replace(r'\s+', ' ', regex=True)

# Verificamos que no hay nulos en la columna 'id'; los removemos
Secciones = Secciones.dropna(subset='id_sede')

# Chequeo de si no hay valores duplicados en la clave
Secciones = Secciones.drop_duplicates(subset=['id_sede', 'nombre'], keep=False)

# Ordenamos alfabéticamente por id
Secciones = Secciones.sort_values(by='id_sede').reset_index(drop=True)

# Chequeamos que no hay duplicados en la clave primaria.
Duplicados = Secciones[Secciones.duplicated(subset=['id_sede', 'nombre'], keep=False)]
assert Duplicados.size == 0, "Error: con clave { id } existen duplicados en la tabla Pais"

# Guardamos la tabla en un archivo .csv
Secciones.to_csv('TablasLimpias/Secciones.csv', index=False)



# %% # ETAPA 2 - Ejecución de los 4 ejercicios de SQL y sus reportes resultantes

'''
    2 - Ejecución de los 4 ejercicios de SQL y sus reportes resultantes

    Prerrequisitos:
            - Haber ejecutado la ETAPA 1 y por tanto que se cuente con las tablas limpias en ./TablasLimpias/
            - Contar con las biliotecas necesarias:
    
    Ejecución:
        Ejecutar el script generará los siguientes reportes (archivos CSV) en la carpeta ./Graficos y Reportes SQL/
            -  'Ejercicio H-I.csv' 
            -  'Ejercicio H-II.csv' 
            -  'Ejercicio H-III.csv' 
            -  'Ejercicio H-IV.csv' 

    Aclaración: El ejercicio H-IV se ejecutará antes que el H-III dado que el último hace uso del reporte generado por el primero
'''

RutaReportesSQL = 'Graficos y Reportes SQL/'

'''
    Ejercicio H.I:
        Para cada país informar cantidad de sedes, cantidad de secciones en promedio que poseen sus sedes y el flujo migratorio
        neto (inmigración - emigración) entre el país y el resto del mundo en el año 2000, ordenado por cantidad de sedes de manera descendiente.

'''

# Importamos bibliotecas.

# Importamos los datasets que vamos a utilizar en este programa.
Migrantes = pd.read_csv("TablasLimpias/Migrantes.csv")
Paises = pd.read_csv("TablasLimpias/Paises.csv")
Regiones = pd.read_csv("TablasLimpias/Regiones.csv")
Secciones = pd.read_csv("TablasLimpias/Secciones.csv")
Sedes = pd.read_csv("TablasLimpias/Sedes.csv")

# Crear una conexión SQLite en memoria.
Connection = sqlite3.connect(':memory:')

# Cargar dfs en la base de datos SQLite.
Migrantes.to_sql('Migrantes', Connection, index=False, if_exists='replace')
Paises.to_sql('Paises', Connection, index=False, if_exists='replace')
Regiones.to_sql('Regiones', Connection, index=False, if_exists='replace')
Secciones.to_sql('Secciones', Connection, index=False, if_exists='replace')
Sedes.to_sql('Sedes', Connection, index=False, if_exists='replace')

# Obtener los Países y su cantidad de Sedes usando la tabla Sedes (no se parte de la tabla Paises dado que 
#   generaría resultados con 0, lo cual no queremos)
Consulta_SQL = """
               SELECT P.codigo_iso AS codigo_iso_pais, COUNT(S.id_sede) AS Cantidad_Sedes
               FROM Paises AS P
               INNER JOIN Sedes AS S ON P.codigo_iso = S.codigo_iso_pais
               GROUP BY P.nombre
               """

# Ejecución de la consulta
SQL_1 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_1.to_sql('SQL_1', Connection, index=False, if_exists='replace')

# Obtener secciones promedio (se utiliza MIN como análogo de ANY_VALUE, ya que dado un id_sede, los países coincidentes serán todos iguales)
Consulta_SQL = """
               SELECT MIN(P.codigo_iso) AS codigo_iso_pais, S1.id_sede, COUNT(S1.nombre) AS Cantidad_Secciones
               FROM Secciones AS S1
               INNER JOIN Sedes AS S2 ON S1.id_sede = S2.id_sede
               INNER JOIN Paises AS P ON S2.codigo_iso_pais = P.codigo_iso
               GROUP BY S1.id_sede
               """

# Ejecución de la consulta
SQL_2 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_2.to_sql('SQL_2', Connection, index=False, if_exists='replace')

# Obtener para cada código de país, la cantidad total de secciones usando el query anterior (SQL_2)
Consulta_SQL = """
               SELECT codigo_iso_pais, SUM(Cantidad_Secciones) AS Cantidad_Secciones_Total
               FROM SQL_2
               GROUP BY codigo_iso_pais
               """

# Ejecución de la consulta
SQL_3 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_3.to_sql('SQL_3', Connection, index=False, if_exists='replace')

# Realizar un JOIN de los queries SQL_1 y SQL_3
Consulta_SQL = """
               SELECT SQL_1.codigo_iso_pais AS codigo_iso_pais,
                      SQL_1.Cantidad_Sedes AS Cantidad_Sedes,
                      ROUND((CAST(SQL_3.Cantidad_Secciones_Total AS float) / CAST(SQL_1.Cantidad_Sedes AS float)), 1) AS Secciones_Promedio
               FROM SQL_1
               INNER JOIN SQL_3 ON SQL_1.codigo_iso_pais = SQL_3.codigo_iso_pais
               """

# Ejecución de la consulta
SQL_4 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_4.to_sql('SQL_4', Connection, index=False, if_exists='replace')


# Obtener el flujo migratorio neto, tomando valores migratorios desde y hacia ARG
Consulta_SQL = """
               SELECT P.codigo_iso AS codigo_iso_pais,
                      (M.inmigrantes - M.emigrantes) AS Flujo_Migratorio_Neto
               FROM Paises AS P
               INNER JOIN Migrantes AS M ON P.codigo_iso = M.id_pais
               WHERE M.anio = 2000
               """

# Ejecución de la consulta
SQL_5 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_5.to_sql('SQL_5', Connection, index=False, if_exists='replace')

# Juntar resultados de SQL_4 y SQL_5 para retornar el valor final
Consulta_SQL = """
               SELECT P.nombre, SQL_4.Cantidad_Sedes, SQL_4.Secciones_Promedio, SQL_5.Flujo_Migratorio_Neto
               FROM SQL_4
               INNER JOIN SQL_5 ON SQL_4.codigo_iso_pais = SQL_5.codigo_iso_pais
               INNER JOIN Paises AS P ON SQL_4.codigo_iso_pais = P.codigo_iso
               ORDER BY SQL_4.Cantidad_Sedes DESC
               """
# Ejecución de la consulta
SQL_6 = pd.read_sql_query(Consulta_SQL, Connection)

# Guardar el reporte resultante
SQL_6.to_csv(RutaReportesSQL + 'Ejercicio H-I.csv', index=False)


'''
    Ejercicio H.II:
        Reportar agrupando por región geográfica: a) la cantidad de países en que Argentina tiene al menos una sede y 
            b) el promedio del flujo migratorio de Argentina hacia esos países en el año 2000 (promedio sobre países donde Argentina tiene sedes) 
            Ordenar de manera descendente por este último campo.

    Aclaración: Se hace uso de las mismas bases de datos ya cargadas (líneas 433-447)
'''

# Obtener los paises con sedes argentinas
Consulta_SQL = """
               SELECT P.codigo_iso AS codigo_iso_pais, 
                      P.id_region AS id_region
               FROM Paises AS P
               INNER JOIN Sedes AS S ON P.codigo_iso = S.codigo_iso_pais
               GROUP BY P.codigo_iso
               HAVING COUNT(S.id_sede) > 0 AND P.id_region IS NOT NULL
               """

# Ejecución de la consulta
SQL_1 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_1.to_sql('SQL_1', Connection, index=False, if_exists='replace')

# Obtener la cantidad de sedes argentinas por región geográfica
Consulta_SQL = """
               SELECT id_region, COUNT(DISTINCT codigo_iso_pais) AS Cantidad_Sedes_ARG_por_region
               FROM SQL_1
               GROUP BY id_region
               """

# Ejecución de la consulta
SQL_2 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_2.to_sql('SQL_2', Connection, index=False, if_exists='replace')

# Obtener la suma por región de migraciones en el año 2000
Consulta_SQL = """
               SELECT P.id_region AS id_region,
                      SUM(M.emigrantes) AS Cantidad_Emigrantes
               FROM Paises AS P
               INNER JOIN Migrantes AS M ON P.codigo_iso = M.id_pais
               WHERE M.anio = 2000 AND P.id_region IS NOT NULL
               GROUP BY P.id_region
               """

# Ejecución de la consulta
SQL_3 = pd.read_sql_query(Consulta_SQL, Connection)
SQL_3.to_sql('SQL_3', Connection, index=False, if_exists='replace')

# Obtener para cada código de país, la cantidad total de secciones usando el query anterior (SQL_2)
Consulta_SQL = """
               SELECT R.nombre, 
                      SQL_2.Cantidad_Sedes_ARG_por_region AS 'Países_con_sedes_argentinas',
                      ROUND((CAST(SQL_3.Cantidad_Emigrantes AS float) / CAST(SQL_2.Cantidad_Sedes_ARG_por_region AS float)), 1) AS 'Flujo_saliente_de_ARG_promedio'
               FROM SQL_2
               INNER JOIN SQL_3 ON SQL_2.id_region = SQL_3.id_region
               INNER JOIN Regiones R ON SQL_2.id_region = R.id
               ORDER BY Flujo_saliente_de_ARG_promedio DESC
               """

# Ejecución de la consulta
SQL_4 = pd.read_sql_query(Consulta_SQL, Connection)

# Guardar el reporte resultante
SQL_4.to_csv(RutaReportesSQL + 'Ejercicio H-II.csv', index=False)


'''
    Ejercicio H.IV:
        Confeccionar un reporte con la información de redes sociales, donde se indique para cada caso: el país, la sede, el tipo de red social y url utilizada.
        Ordenar de manera ascendente por nombre de país, sede, tipo de red y finalmente por url.

    Aclaración: se decidió ejecutar el ejercicio H.IV antes que el H.III dado que este último hace uso del reporte generado por el primero
        Además, se hace uso de las mismas bases de datos ya cargadas (líneas 433-447) y se adiciona la carga de la tabla Redes_Sociales.csv
'''

# Carga de datasets necesarios
Redes_Sociales_DB = pd.read_csv('TablasLimpias/Redes_Sociales.csv')

#Sedes[['id_sede', 'redes_sociales']]

Redes_FB = [] # Facebook.
Redes_TW = [] # Twitter.
Redes_IG = [] # Instragram.
Redes_YT = [] # YouTube.
Redes_LI = [] # Linkedin.
Redes_FR = [] # Flickr.
Redes_Invalidas = [] # Links mal formados o @ ambiguos (Instagram o Twitter).
Redes_NULL = [] # Sede sin link.

Redes_Totales = [] # Redes totales.

for Sede_Id, URL in zip(Redes_Sociales_DB['id_sede'], Redes_Sociales_DB['URL']):
    URL_Lista = str(URL).split('  //  ') # Lista con las redes sociales de esa sede (puede estar vacía).

    for URL in URL_Lista:

        # Por el formato, si hay links el strip introduce un dato extra que siempre es el string vacío. Con esto, lo eliminamos.
        if(URL == ''): continue 

        URL = URL.strip() # Quitar espacios al inicio y al final.
        URL = URL.lower() # Que empiece siempre en minúscula para mayor consistencia (hay datos que se escapaban a esto y se filtraban mal).
        
        if(URL == 'nan'):
            Redes_NULL.append(Sede_Id)   # Sedes sin redes.
            continue
        else: 
            Redes_Totales.append((Sede_Id, URL))  # Sedes con redes.

        # Clasificar redes en distintas listas.
        if(URL[0] =='@' or ' ' in URL or ".com" not in URL): 
            Redes_Invalidas.append((Sede_Id, URL))
        elif 'facebook' in URL: 
            Redes_FB.append((Sede_Id, URL))
        elif('twitter' in URL): 
            Redes_TW.append((Sede_Id, URL))
        elif('instagram' in URL): 
            Redes_IG.append((Sede_Id, URL))
        elif('linkedin' in URL): 
            Redes_LI.append((Sede_Id, URL))
        elif('flickr' in URL): 
            Redes_FR.append((Sede_Id, URL))
        elif('youtube' in URL): 
            Redes_YT.append((Sede_Id, URL))

# Redes a almacenar.
Redes_Validas = Redes_FB + Redes_TW + Redes_IG + Redes_LI + Redes_FR + Redes_YT

# Redes que no se usan.
Redes_Descartadas = set(Redes_Totales).difference(set(Redes_FB)).difference(set(Redes_IG)).difference(set(Redes_LI)).difference(set(Redes_FR)).difference(set(Redes_YT)).difference(set(Redes_TW)).difference(set(Redes_Invalidas))

# Creación de listas de almacenamiento.
Sede_IDs = []
Redes_Sociales = []
URLs = []

# Creación de diccionario vacío.
Dic_Redes = {'id_sede': Sede_IDs, 'red_social': Redes_Sociales, 'url': URLs}

# Relleno del diccionario con el id_sede, red_social y url.
for Sede_Id, Url in Redes_FB:
    Dic_Redes['id_sede'].append(Sede_Id)
    Dic_Redes['red_social'].append('facebook')
    Dic_Redes['url'].append(Url)

for Sede_Id, Url in Redes_TW:
    Dic_Redes['id_sede'].append(Sede_Id)
    Dic_Redes['red_social'].append('twitter')
    Dic_Redes['url'].append(Url)

for Sede_Id, Url in Redes_IG:
    Dic_Redes['id_sede'].append(Sede_Id)
    Dic_Redes['red_social'].append('instagram')
    Dic_Redes['url'].append(Url)

for Sede_Id, Url in Redes_YT:
    Dic_Redes['id_sede'].append(Sede_Id)
    Dic_Redes['red_social'].append('youtube')
    Dic_Redes['url'].append(Url)

for Sede_Id, Url in Redes_FR:
    Dic_Redes['id_sede'].append(Sede_Id)
    Dic_Redes['red_social'].append('flickr')
    Dic_Redes['url'].append(Url)

for Sede_Id, Url in Redes_LI:
    Dic_Redes['id_sede'].append(Sede_Id)
    Dic_Redes['red_social'].append('linkedin')
    Dic_Redes['url'].append(Url)

# Formar df con el diccionario.
Redes_DF = pd.DataFrame(Dic_Redes)

# Consulta SQL.
Query =  '''
          SELECT p.nombre AS pais,
                 r.id_sede AS sede,
                 r."red_social",
                 r.url
          FROM Redes_DF AS r
          INNER JOIN Sedes AS s ON s.id_sede = r.id_sede
          LEFT JOIN Paises AS p ON s.codigo_iso_pais = p.codigo_iso
          ORDER BY pais ASC, sede ASC, "red_social" ASC, url ASC

'''

Tabla = sqldf(Query)

# Guardar archivo.
Tabla.to_csv(RutaReportesSQL + 'Ejercicio H-IV.csv', index=False)


'''
    Ejercicio H.III:
        Confeccionar un reporte con la información de para cada país y la cantidad de tipos de redes distintas utilizadas.

    Aclaración: Se hace uso de las mismas bases de datos ya cargadas (líneas 433-447 y línea 609) y se adiciona la carga del reporte Ejercicio H-IV.csv (ejercicio anterior)
'''

Reporte_H_IV = pd.read_csv(RutaReportesSQL + 'Ejercicio H-IV.csv')

# Consulta a la tabla resultante del punto h.iv.
# Con esto se forma una nueva tabla con el pais y la red social.

Query =  '''
          SELECT DISTINCT pais, "red_social" 
          FROM Reporte_H_IV
          ORDER BY pais ASC

'''

SQL_1 = sqldf(Query)

# Consulta a la tabla resultante para obtener la cantidad de tipo de redes.
Query =  '''
          SELECT DISTINCT pais, Count("red_social") AS Cantidad_Tipo_Redes
          FROM SQL_1
          GROUP BY pais
          ORDER BY Cantidad_Tipo_Redes DESC, pais ASC

'''

SQL_2 = sqldf(Query)

# Guardar archivo.
SQL_2.to_csv(RutaReportesSQL + 'Ejercicio H-III.csv', index=False)



# %% # ETAPA 3 - Generación de gráficos en base a los puntos anteriores

'''
    3 - Generación de gráficos en base a los puntos anteriores
    
    Prerrequisitos:
            - Haber ejecutado la ETAPA 1 y por tanto que se cuente con las tablas limpias en ./TablasLimpias/
            - Contar con las biliotecas necesarias

    Descripción:
        El script toma los archivos provistos y en base a ellos crea nuevas tablas y grafica las variables solicitadas en el informe.
        Las etapas son:
            1) Carga de datasets y bibliotecas
            2) Gráfico correspondiente al punto i
            3) Gráfico correspondiente al punto ii
            4) Gráfico correspondiente al punto iii

    Ejecución:
        Ejecutar el script en consola generará los gráficos en la carpeta ./Graficos y Reportes SQL/

    Aclaración: Se hace uso de las mismas bases de datos ya cargadas (líneas 444-458 y línea 615)
'''

RutaGraficos = RutaReportesSQL

'''
    Punto I.I. Mostrar cantidad de sedes por región geográfica
'''

Consulta_SQL = """
               SELECT R.nombre AS region,
                      COUNT(S.id_sede) AS cantidad_sedes
               FROM Paises AS P
               INNER JOIN Sedes AS S ON P.codigo_iso = S.codigo_iso_pais
               LEFT JOIN (
                            SELECT SC.id_sede, COUNT(SC.id_sede) AS cant_secciones
                            FROM Secciones AS SC
                            GROUP BY SC.id_sede
                         ) AS CS ON S.id_sede = CS.id_sede
               LEFT JOIN Regiones AS R ON P.id_region = R.id
               GROUP BY R.nombre
               ORDER BY cantidad_sedes DESC;
               
               """

# Armamos el DataFrame con los la cantidad de sedes, el promedio de secciones y el flujo migratorio neto por país.
Sedes_Por_Regiones = pd.read_sql_query(Consulta_SQL, Connection)

# Cambios en los textos para que queden más prolijo en el gráfico.
Sedes_Por_Regiones['region'] = Sedes_Por_Regiones['region'].apply(lambda x: x.title())
Sedes_Por_Regiones['region'] = Sedes_Por_Regiones['region'].apply(lambda x: x.replace(' Y ', ' y ') if ' Y ' in x else x)
Sedes_Por_Regiones['region'] = Sedes_Por_Regiones['region'].apply(lambda x: x.replace(' Del ', ' del ') if ' Del ' in x else x)

# Crear la figura y ajustar el tamaño.
Figure, Graphic_1 = plt.subplots(figsize=(10, 10))

# Ajustar la fuente global.
plt.rcParams['font.family'] = 'sans-serif'

# Dibujar el gráfico de barras.
Graphic_1.bar(Sedes_Por_Regiones['region'], Sedes_Por_Regiones['cantidad_sedes'])

# Título y etiquetas con mejor formato.
Graphic_1.set_xlabel('Regiones geográficas', fontsize=12, labelpad=10)
Graphic_1.set_ylabel('Cantidad de sedes', fontsize=12, labelpad=10)

# Establecer límite del eje Y dinámicamente.
Graphic_1.set_ylim(0, max(Sedes_Por_Regiones['cantidad_sedes']) + 10)

# Mostrar etiquetas de las barras con el valor exacto.
Graphic_1.bar_label(Graphic_1.containers[0], fontsize=10, padding=5)

# Rotar etiquetas del eje X.
Graphic_1.set_xticklabels(Sedes_Por_Regiones['region'], rotation=90, ha='right')

# Ajustar los márgenes para evitar que las etiquetas se corten.
plt.tight_layout()

# Guardar gráficos.
plt.savefig(RutaGraficos + 'Punto i.png')

# Mostrar el gráfico.
#plt.show()


'''
    Punto I.II. Boxplot, por cada región geográfica, del valor correspondiente al promedio del flujo migratorio de los países en donde Argentina tiene una delegación.
'''

# Recolectamos países que tienen sedes.
Paises_Con_Sedes = list(Sedes['codigo_iso_pais'].unique())

# Filtramos df Migrantes con los países que tienen sedes.
Migrantes_Con_Sedes = Migrantes[Migrantes['id_pais'].isin(Paises_Con_Sedes)]

# Creamos la columna "Flujo Neto".
Migrantes_Con_Sedes.loc[:, 'Flujo_Neto'] = Migrantes_Con_Sedes.loc[:, 'inmigrantes'] - Migrantes_Con_Sedes.loc[:, 'emigrantes']

# Agrupar por país y calcular el promedio del flujo neto en los distintos años.
Migrantes_Con_Sedes = Migrantes_Con_Sedes.groupby('id_pais', as_index=False)['Flujo_Neto'].mean()

# Vinculamos la tabla con Paises y Regiones para hallar las Regiones.
Migrantes_Con_Sedes = Migrantes_Con_Sedes.merge(Paises, how='left', left_on='id_pais', right_on='codigo_iso')
Migrantes_Con_Sedes = Migrantes_Con_Sedes.merge(Regiones, how='left', left_on='id_region', right_on='id')

# Filtramos columnas.
Migrantes_Con_Sedes = Migrantes_Con_Sedes[['nombre_y', 'id_pais', 'Flujo_Neto']]

# Cambiamos los nombres de las columnas.
Migrantes_Con_Sedes.rename(columns={'nombre_y': 'region'}, inplace=True)

# Damos formato a los nombres de las regiones para que se vean bien en el gráfico.
Migrantes_Con_Sedes['region'] = Migrantes_Con_Sedes['region'].apply(lambda x: x.title())
Migrantes_Con_Sedes['region'] = Migrantes_Con_Sedes['region'].apply(lambda x: x.replace(' Y ', ' y ') if ' Y ' in x else x)
Migrantes_Con_Sedes['region'] = Migrantes_Con_Sedes['region'].apply(lambda x: x.replace(' Del ', ' del ') if ' Del ' in x else x)

# Remover datos que molestan.
Migrantes_Con_Sedes = Migrantes_Con_Sedes[Migrantes_Con_Sedes['id_pais'] != 'ITA']
Migrantes_Con_Sedes = Migrantes_Con_Sedes[Migrantes_Con_Sedes['id_pais'] != 'ESP']

# Función para eliminar outliers de un dataframe basándose en una columna.
def Eliminar_Outliers(df: pd.DataFrame, Columna: str) -> pd.DataFrame:

    # Calcular Q1 y Q3.
    Q1 = df[Columna].quantile(0.25)
    Q3 = df[Columna].quantile(0.75)
    IQR = Q3 - Q1  # Rango intercuartil.

    # Definir los límites para los outliers.
    Limite_Inferior = Q1 - 1.5 * IQR
    Limite_Superior = Q3 + 1.5 * IQR

    # Filtrar dataframe.
    df = df[(df[Columna] >= Limite_Inferior) & (df[Columna] <= Limite_Superior)]

    return df

# Definimos listas para separar los boxplots.
Regiones_Con_Mas_Flujo = ['América del Sur', 'América del Norte']
Regiones_Con_Menor_Flujo = [Region for Region in Migrantes_Con_Sedes['region'].unique() if Region not in Regiones_Con_Mas_Flujo]

# Crear DataFrames separados.
df_Regiones_Con_Mas_Flujo = Migrantes_Con_Sedes[Migrantes_Con_Sedes['region'].isin(Regiones_Con_Mas_Flujo)]
df_Regiones_Con_Menor_Flujo = Migrantes_Con_Sedes[Migrantes_Con_Sedes['region'].isin(Regiones_Con_Menor_Flujo)]

# Eliminamos outliers nuevamente en las de menor flujo para un mejor visionado.
df_Regiones_Con_Menor_Flujo = Eliminar_Outliers(df_Regiones_Con_Menor_Flujo, 'Flujo_Neto')

# Obtener las medianas para ordenar las regiones en el gráfico.
Medianas_Mayor_Flujo = df_Regiones_Con_Mas_Flujo.groupby('region')['Flujo_Neto'].median().sort_values().index.tolist()
Medianas_Menor_Flujo = df_Regiones_Con_Menor_Flujo.groupby('region')['Flujo_Neto'].median().sort_values().index.tolist()

# Creamos los gráficos: dos paneles.
Figure, Graficos = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

# Primer boxplot.
sns.boxplot(x='region', y='Flujo_Neto', data=df_Regiones_Con_Mas_Flujo, ax=Graficos[0], order=Medianas_Mayor_Flujo, palette='Set2')
Graficos[0].set_xlabel('Region', labelpad = 90)
Graficos[0].set_ylabel('Promedio de flujo migratorio neto')
Graficos[0].set_xticklabels(Graficos[0].get_xticklabels(), rotation=90, ha='right')  # Rotate x-axis labels
Graficos[0].grid(False) # Eliminar la cuadrícula
Graficos[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".") ))

# Segundo boxplot.
sns.boxplot(x='region', y='Flujo_Neto', data=df_Regiones_Con_Menor_Flujo, ax=Graficos[1], order=Medianas_Menor_Flujo, palette='Set1')
Graficos[1].set_xlabel('Region', labelpad = 50)
Graficos[1].set_ylabel('Promedio de flujo migratorio neto')
Graficos[1].set_xticklabels(Graficos[1].get_xticklabels(), rotation=90, ha='right')  # Rotate x-axis labels
Graficos[1].grid(False)  # Eliminar la cuadrícula
Graficos[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".") ))

# Ajustar los márgenes para evitar que las etiquetas se corten.
plt.tight_layout()

# Guardar gráficos.
plt.savefig(RutaGraficos + 'Punto ii.png')

# Show the plots
#plt.show()


'''
    Punto I.III. Relación entre el flujo migratorio desde cada país hacia Argentina y la cantidad de sedes en el exterior que tiene Argentina en esos países
'''

Consulta_SQL = """
               SELECT M.id_pais, M.inmigrantes, COUNT(S.id_sede) AS cantidad_sedes
               FROM Migrantes AS M
               LEFT JOIN Paises AS P ON M.id_pais = P.codigo_iso
               INNER JOIN Sedes AS S ON M.id_pais = S.codigo_iso_pais
               WHERE anio = 2000
               GROUP BY M.id_pais
               ORDER BY M.inmigrantes DESC
               """

Flujo_Migratorio_2000 = pd.read_sql_query(Consulta_SQL, Connection)
Flujo_Migratorio_2000.head(10)
import numpy as np 

# Crear la figura y ajustar el tamaño.
Figure, Graphic_1 = plt.subplots(figsize=(10, 6))

plt.rcParams['font.family'] = 'sans-serif'

# Graficar los datos.
Graphic_1.plot('cantidad_sedes', 'inmigrantes', data=Flujo_Migratorio_2000, marker="o", linestyle='',
               markersize=10, label = '')

# Calcular la línea de tendencia (regresión lineal).
x = Flujo_Migratorio_2000['cantidad_sedes']
y = Flujo_Migratorio_2000['inmigrantes']
Slope, Intercept = np.polyfit(x, y, 1)
Trendline = Slope * x + Intercept

# Calcular R² (coeficiente de determinación).
Correlation_Matrix = np.corrcoef(x, y)
R_value = Correlation_Matrix[0, 1]**2  # R²

# Graficar la línea de tendencia.
Graphic_1.plot(x, Trendline, color='red', linestyle='--', label=f'R² = {R_value:.2f}')

# Etiquetas y título.
Graphic_1.set_ylabel('Inmigrantes', fontsize='medium', labelpad=15)
Graphic_1.set_xlabel('Cantidad de sedes', fontsize='medium', labelpad=15)

# Agregar separador de miles al eje Y.
Graphic_1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".") ))

# Ajustar el diseño para evitar recortes.
plt.tight_layout()

# Mostrar leyenda.
Graphic_1.legend()

# Guardar gráficos.
plt.savefig(RutaGraficos + 'Punto iii.png')

# Mostrar el gráfico.
#plt.show()
