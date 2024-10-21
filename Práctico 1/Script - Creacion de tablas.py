'''
    Script para la generación automática de tablas descritas en nuestro modelo basado en los datasets de migraciones, sedes y secciones.
    
    Prerrequisitos:
        Los archivos necesarios descritos en el enunciado del Trabajo Práctico estarán ubicados dentro de la carpeta Materiales/
            - Migraciones.csv
            - lista-sedes-datos.csv
            - lista-secciones.csv
        En el caso de lista-sedes.csv, no será utilizado ya que lista-sedes-datos.csv lo contiene en los datos que nos interesan
    
    Descripción:
        El script toma los archivos provistos y en base a ellos crea nuevas tablas basadas en el modelo DER que especificamos en el informe.
        Las etapas son:
            1) Creación de tabla Migrantes.csv (basado en Migraciones.csv)
            2) Creación de tabla 

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

# Guardamos el archivo
# Migrantes.to_csv('Tablas/TABLA. Migrantes.csv', index=False)

Migrantes_.to_csv('Tablas/TABLA. Migrantes - Diseño 2.csv', index=False)