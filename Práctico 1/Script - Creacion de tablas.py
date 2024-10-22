'''
    Script para la generación automática de tablas descritas en nuestro modelo basado en los datasets de migraciones, sedes y secciones.
    
    Prerrequisitos:
        Los archivos necesarios descritos en el enunciado del Trabajo Práctico estarán ubicados dentro de la carpeta Materiales/
            - Migraciones.csv
            - lista-sedes-datos.csv*
            - lista-secciones.csv
        *) Es importante antes de usar el script corregir la linea 16 de lista-sedes-datos.csv:
            Remover el "", justo antes de "VII  Región  del  Maule;  VIII  Región  del  Bio  Bio;  IX  Region  de  la  Araucania;  XVI  Region  de  Ñuble"
        **) El archivo lista-sedes.csv no será utilizado porque lista-sedes-datos.csv lo incluye en los valores que consideramos importantes

    Descripción:
        El script toma los archivos provistos y en base a ellos crea nuevas tablas basadas en el modelo DER que especificamos en el informe.
        Las etapas son:
            1) Creación de tabla Migrantes.csv (basado en Migraciones.csv)
            2) Creación de tabla Regiones.csv (basado en lista-sedes-datos.csv)

    Ejecución:
        Ejecutar el script en consola generará las tablas en la carpeta Output/
'''

import pandas as pd

# Carga de datasets
Ruta = 'Materiales/'
Dataset_Migraciones = 'Migraciones.csv'
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

# Hay una fila que tiene a ARG de los dos lados: la borramos
Migrantes = Migrantes[~((Migrantes['id_pais_origen'] == 'ARG') & (Migrantes['id_pais_destino'] == 'ARG'))]

# Creamos cinco DataFrames, cada uno representando dado un origen y un destino, la cantidad de migrantes en un año específico (le agregamos una columna con el año correspondiente).
# Luego, los filtramos: nos quedamos sólo con las filas con valores mayores a 0, es decir, con filas que tengan migrantes. 
# Reseteamos el índice y les cambiamos el nombre. Por último, los concatenamos en el DataFrame final.

DataFrames_Cantidades = []

for Columna in Columnas_Numericas:
    DataFrame = Migrantes[['id_pais_origen', 'id_pais_destino', Columna]]    # Filtrado de columnas.
    DataFrame = DataFrame[DataFrame[Columna] > 0]                            # Filtrado de filas.
    DataFrame['anio'] = Columna[-4:len(Columna)+1]                           # Crear columna con el año.    
    DataFrame = DataFrame.reset_index(drop=True)                             # Resetear índices.
    DataFrame = DataFrame.rename(columns={Columna: 'migrantes'})             # Renombrar columna.
    DataFrames_Cantidades.append(DataFrame)                                  # Agregar df a lista de dfs.

Migrantes = pd.concat(DataFrames_Cantidades)

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
Migrantes_.to_csv('Tablas/Migrantes.csv', index=False)



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
Regiones.to_csv('Tablas/Regiones.csv', index=False)


'''
    Etapa 3: Creación de la tabla Paises
'''

# Usamos los códigos y nombres de la base de datos "Migraciones.csv", ya que son más exhaustivos que los de las otras tablas. 
# El procedimiento para encontrar los valores únicos es:
#   1. Armar tres DataFrames: uno con los países de origen -código y nombre-, otro con los países de destino -código y nombre- 
#       y otro con los países de "Sedes". De esa forma obtenemos todos los países que están en una u otra columna pero no en las otras.
#   2. Concatenarlos verticalmente, llamando las columnas "id" (el código ISO del país) y "nombre". Este DataFrame se llamará Países.
#   3. Se eliminan las filas con valores duplicados en la columna "id".

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

# Filtramos los valores repetidos de las columna "id". Además, reseteamos el índice
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
Paises = Paises.rename(columns={'id_x': 'id', 'nombre_x': 'nombre', 'id_y': 'id_region'})

########## SOLUCIONAR TEMA CON LOS NULLS



