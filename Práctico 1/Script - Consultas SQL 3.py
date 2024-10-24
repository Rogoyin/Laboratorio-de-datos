# Carga de bibliotecas.

import pandas as pd
from inline_sql import sql, sql_val
from pandasql import sqldf

# Carga de datasets necesarios.

Sedes = pd.read_csv('Tablas/Sedes.csv')
Secciones = pd.read_csv('Tablas/Secciones.csv')
Migrantes = pd.read_csv('Tablas/Migrantes.csv')
Redes_Sociales_DB = pd.read_csv('Tablas/Redes_Sociales.csv')
H_IV = pd.read_csv('Tablas/h.iv.csv')

# Consulta a la tabla resultante del punto h.iv.
# Con esto se forma una nueva tabla con el pais y la red social.

Query =  '''
          SELECT DISTINCT pais, "red_social" 
          FROM H_IV
          ORDER BY pais ASC

'''

H_IV2 = sqldf(Query)

# Consulta a la tabla resultante para obtener la cantidad de tipo de redes.
Query =  '''
          SELECT DISTINCT pais, Count("red_social") AS Cantidad_Tipo_Redes
          FROM H_IV2
          GROUP BY pais
          ORDER BY Cantidad_Tipo_Redes DESC, pais ASC

'''

H_IV2 = sqldf(Query)
H_IV2.to_csv('Tablas/h.iii.csv')