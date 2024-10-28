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

import pandas as pd

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
