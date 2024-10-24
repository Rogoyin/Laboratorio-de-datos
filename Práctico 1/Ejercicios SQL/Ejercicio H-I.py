'''
    Autores:
        - Alvarez, Matías
        - Dumas, Román
        - Nogueroles, Patricio
    
    Ejercicio H.I:
        Para cada país informar cantidad de sedes, cantidad de secciones en promedio que poseen sus sedes y el flujo migratorio
        neto (inmigración - emigración) entre el país y el resto del mundo en el año 2000, ordenado por cantidad de sedes de manera descendiente.

        Prerrequisitos:
            - Haber ejecutado el script 'Script - Creacion de tablas.py' y contar con las tablas resultantes en ./Tablas/
    
        Ejecución:
            Ejecutar el script generará el reporte 'Ejercicio H-I.csv' en la carpeta ./Reportes/
'''

# Importamos bibliotecas.

import pandas as pd
from inline_sql import sql, sql_val
import sqlite3

# Importamos los datasets que vamos a utilizar en este programa.

Migrantes = pd.read_csv("Tablas/Migrantes.csv")
Paises = pd.read_csv("Tablas/Paises.csv")
Regiones = pd.read_csv("Tablas/Regiones.csv")
Secciones = pd.read_csv("Tablas/Secciones.csv")
Sedes = pd.read_csv("Tablas/Sedes.csv")

# Crear una conexión SQLite en memoria.
Connection = sqlite3.connect(':memory:')

# Cargar dfs en la base de datos SQLite.
Migrantes.to_sql('Migrantes', Connection, index=False, if_exists='replace')
Paises.to_sql('Paises', Connection, index=False, if_exists='replace')
Regiones.to_sql('Regiones', Connection, index=False, if_exists='replace')
Secciones.to_sql('Secciones', Connection, index=False, if_exists='replace')
Sedes.to_sql('Sedes', Connection, index=False, if_exists='replace')

Consulta_SQL = """
               SELECT P.nombre AS pais, 
                      COUNT(S.id) AS cantidad_sedes, 
                      COALESCE(AVG(CS.cant_secciones), 0) AS secciones_promedio,
                      COALESCE(M.neto_migratorio, 0) AS "flujo migratorio neto"
               FROM Paises AS P
               INNER JOIN Sedes AS S ON P.id = S.id_pais
               LEFT JOIN (
                            SELECT SC.id_sede, COUNT(SC.id_sede) AS cant_secciones
                            FROM Secciones AS SC
                            GROUP BY SC.id_sede
                         ) AS CS ON S.id = CS.id_sede
               LEFT JOIN (
                            SELECT id_pais, (inmigrantes - emigrantes) AS neto_migratorio
                            FROM Migrantes
                            WHERE anio = 2000
                          ) AS M ON P.id = M.id_pais
               GROUP BY P.nombre
               ORDER BY cantidad_sedes DESC, pais;
               
               """

# Ejecución de la consulta
SQL_1 = pd.read_sql_query(Consulta_SQL, Connection)

# Guardar el reporte resultante
SQL_1.to_csv('Reportes/Ejercicio H-I.csv', index=False)
