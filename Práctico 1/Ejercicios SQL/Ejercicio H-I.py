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
            - Contar con las biliotecas necesarias
    
        Ejecución:
            Ejecutar el script generará el reporte 'Ejercicio H-I.csv' en la carpeta ./Reportes/
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
SQL_6.to_csv('Reportes/Ejercicio H-I.csv', index=False)