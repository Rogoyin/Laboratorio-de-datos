'''
    Autores:
        - Alvarez, Matías
        - Dumas, Román
        - Nogueroles, Patricio
    
    Ejercicio H.IV:
        Confeccionar un reporte con la información de redes sociales, donde se indique para cada caso: el país, la sede, el tipo de red social y url utilizada.
        Ordenar de manera ascendente por nombre de país, sede, tipo de red y finalmente por url.

        Prerrequisitos:
            - Haber ejecutado el script 'Script - Creacion de tablas.py' y contar con las tablas resultantes en ./Tablas/
            - Contar con las biliotecas necesarias
    
        Ejecución:
            Ejecutar el script generará el reporte 'Ejercicio H-IV.csv' en la carpeta ./Reportes/
'''

# Carga de bibliotecas.

import pandas as pd
# from inline_sql import sql, sql_val
from pandasql import sqldf

# Carga de datasets necesarios.

Sedes = pd.read_csv('../Tablas/Sedes.csv')
Secciones = pd.read_csv('../Tablas/Secciones.csv')
Migrantes = pd.read_csv('../Tablas/Migrantes.csv')
Redes_Sociales_DB = pd.read_csv('../Tablas/Redes_Sociales.csv')

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
          SELECT s.nombre AS pais,
                 r.id_sede AS sede,
                 r."red_social",
                 r.url
          FROM Redes_DF AS r
          INNER JOIN Sedes AS s ON s.id_sede = r.id_sede
          ORDER BY pais ASC, sede ASC, "red_social" ASC, url ASC
'''

Tabla = sqldf(Query)

# Guardar archivo.
Tabla.to_csv('Reportes/Ejercicio H-IV.csv')