import pandas as pd
from inline_sql import sql, sql_val
from pandasql import sqldf

sedes_basico = pd.read_csv('Materiales/lista-sedes.csv')
sedes_completo = pd.read_csv('lista-sedes-datos.csv')
sedes_secciones = pd.read_csv('lista-secciones.csv')
migracionesDF = pd.read_csv('datos_migraciones.csv')


sedes_completo[['sede_id', 'redes_sociales']]

#Nuevo
redes_FB = []
redes_TW = []
redes_IG = [] #pueden aparecer solo con un "@"
redes_YT = []
redes_LI = [] #linkedin...
redes_FR = [] #... Flickr.....
redes_Invalidas = [] #link mal formado o @ ambiguo (IG o Twitter)
redes_NULL = [] #sede sin link

redes_totales = []

for sede_id, redes in zip(sedes_completo['sede_id'], sedes_completo['redes_sociales']):
  print(redes)
  redes = str(redes).split('  //  ') #lista con las redes sociales de esa sede (puede ser vacía)

  for red in redes:

    if(red == ''): continue #por el formato, si hay links el strip me introduce un dato extra que siempre es el string vacío. lo quito acá

    red = red.strip() #quito espacios al inicio y al final
    red = red[0].lower() + red[1:] #Que empiece siempre en minus para mas consistencia (hay datos que se escapaban a esto y se filtraban mal)

    if(red == 'nan'):
      redes_NULL.append(sede_id)
      continue
    else: redes_totales.append((sede_id,red))

    if(red[0] =='@' or ' ' in red or not '.com' in red): redes_Invalidas.append((sede_id, red))
    elif('facebook' in red): redes_FB.append( (sede_id, red))
    elif('twitter' in red): redes_TW.append((sede_id, red) )
    elif('instagram' in red): redes_IG.append((sede_id, red) )
    elif('linkedin' in red): redes_LI.append((sede_id, red) )
    elif('flickr' in red): redes_FR.append((sede_id, red) )
    elif('youtube' in red): redes_YT.append((sede_id, red) )

redes_validas = redes_FB+ redes_TW + redes_IG + redes_LI + redes_FR + redes_YT

redes_descartadas = set(redes_totales).difference(set(redes_FB)).difference(set(redes_IG)).difference(set(redes_LI)).difference(set(redes_FR)).difference(set(redes_YT)).difference(set(redes_TW)).difference(set(redes_Invalidas))

#Creo un diccionario de sede_id a red social. Notar que puede ser multivaluado por las varias cuentas de IG de una sola sede

#Esto lo podía hacer directo en el ciclo de arriba y no dar tantas vueltas como estoy haciendo
#pero quería controlar que esté leyendo bien los datos de la tabla y lo de arriba era más directo para verificar eso

#sede_id, Red, URL
sede_ids = []
redess = []
URLS = []

dic_redes = {'sede_id': sede_ids, 'Red Social': redess, 'URL': URLS}

for sede_id, url in redes_FB:
  dic_redes['sede_id'].append(sede_id)
  dic_redes['Red Social'].append('Facebook')
  dic_redes['URL'].append(url)

for sede_id, url in redes_TW:
  dic_redes['sede_id'].append(sede_id)
  dic_redes['Red Social'].append('Twitter')
  dic_redes['URL'].append(url)

for sede_id, url in redes_IG:
  dic_redes['sede_id'].append(sede_id)
  dic_redes['Red Social'].append('Instagram')
  dic_redes['URL'].append(url)

for sede_id, url in redes_YT:
  dic_redes['sede_id'].append(sede_id)
  dic_redes['Red Social'].append('Youtube')
  dic_redes['URL'].append(url)

for sede_id, url in redes_FR:
  dic_redes['sede_id'].append(sede_id)
  dic_redes['Red Social'].append('Flickr')
  dic_redes['URL'].append(url)

for sede_id, url in redes_LI:
  dic_redes['sede_id'].append(sede_id)
  dic_redes['Red Social'].append('Linkedin')
  dic_redes['URL'].append(url)

Redes_DF = pd.DataFrame(dic_redes)
Redes_DF

#Si tuviera atributos multivaluados, este comando me los separa en entradas nuevas por cada valor
#Redes_DF.explode('URL')

sedes_basico.sample(2)

#A la tabla de arriba, le hacemos un JOIN con la tabla de paises, para conseguir la columna en el formato que nos piden

#La tabla "sedes_basico" tiene el nombre de cada id de pais

#Ordenar de manera ascendente por nombre de país, sede, tipo de red y
#finalmente por url. Ejemplo:



query =  '''
          SELECT s.pais_castellano AS País,
                 r.sede_id AS Sede,
                 r."Red Social",
                 r.URL
                 FROM Redes_DF AS r

          INNER JOIN sedes_basico AS s
          ON s.sede_id = r.sede_id

          ORDER BY País ASC, Sede ASC, "Red Social" ASC, URL ASC
'''
out = sqldf(query)
out.to_csv('Redes Sociales - Ejercicio h.iv')