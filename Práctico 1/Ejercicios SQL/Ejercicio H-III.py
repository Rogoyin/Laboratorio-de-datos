'''
    Autores:
        - Alvarez, Matías
        - Dumas, Román
        - Nogueroles, Patricio
    
    Ejercicio H.III:
        Confeccionar un reporte con la información de para cada país y la cantidad de tipos de redes distintas utilizadas.

        Prerrequisitos:
            - Haber ejecutado el script 'Ejercicio H.IV.py' y contar con las tablas resultantes en /Reportes/
            - Contar con las biliotecas necesarias
    
        Ejecución:
            Ejecutar el script generará el reporte 'Ejercicio H-III.csv' en la carpeta ./Reportes/
'''

# Carga de bibliotecas.

import pandas as pd
from inline_sql import sql, sql_val
from pandasql import sqldf

# Carga de datasets necesarios.

Sedes = pd.read_csv('../Tablas/Sedes.csv')
Secciones = pd.read_csv('../Tablas/Secciones.csv')
Migrantes = pd.read_csv('../Tablas/Migrantes.csv')
Redes_Sociales_DB = pd.read_csv('../Tablas/Redes_Sociales.csv')
H_IV = pd.read_csv('Reportes/Ejercicio H-IV.csv')

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

# Guardar archivo.
H_IV2.to_csv('Reportes/Ejercicio H-III.csv')