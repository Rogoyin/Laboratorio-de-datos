'''
    Autores:
        - Alvarez, Matías
        - Dumas, Román
        - Nogueroles, Patricio
    
    Ejercicio H.I:
        Reportar agrupando por región geográfica: a) la cantidad de países en que Argentina tiene al menos una sede y 
            b) el promedio del flujo migratorio de Argentina hacia esos países en el año 2000 (promedio sobre países donde Argentina tiene sedes) 
            Ordenar de manera descendente por este último campo.
    
        Prerrequisitos:
            - Haber ejecutado el script 'Script - Creacion de tablas.py' y contar con las tablas resultantes en ./Tablas/
            - Contar con las biliotecas necesarias
    
        Ejecución:
            Ejecutar el script generará el reporte 'Ejercicio H-II.csv' en la carpeta ./Reportes/
'''

# Importamos bibliotecas.
import pandas as pd
#from inline_sql import sql, sql_val
import sqlite3

# Importamos los datasets que vamos a utilizar en este programa.
Migrantes = pd.read_csv("../Tablas/Migrantes.csv")
Paises = pd.read_csv("../Tablas/Paises.csv")
Regiones = pd.read_csv("../Tablas/Regiones.csv")
Secciones = pd.read_csv("../Tablas/Secciones.csv")
Sedes = pd.read_csv("../Tablas/Sedes.csv")

# Crear una conexión SQLite en memoria.
Connection = sqlite3.connect(':memory:')

# Cargar dfs en la base de datos SQLite.
Migrantes.to_sql('Migrantes', Connection, index=False, if_exists='replace')
Paises.to_sql('Paises', Connection, index=False, if_exists='replace')
Regiones.to_sql('Regiones', Connection, index=False, if_exists='replace')
Secciones.to_sql('Secciones', Connection, index=False, if_exists='replace')
Sedes.to_sql('Sedes', Connection, index=False, if_exists='replace')

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
SQL_4.to_csv('Reportes/Ejercicio H-II.csv', index=False)