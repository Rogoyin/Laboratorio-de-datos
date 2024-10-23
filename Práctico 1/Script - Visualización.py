'''
    Autores:
    - Alvarez, Matías
    - Dumas, Román
    - Nogueroles, Patricio

    Script para la generación de gráficos.
    
    Prerrequisitos:
        Los archivos necesarios estarán ubicados dentro de la carpeta Tablas/
            - Migraciones.csv
            - Sedes.csv
            - Secciones.csv
            - Redes_Sociales.csv
            - Regiones.csv
            - Paises.csv

    Descripción:
        El script toma los archivos provistos y en base a ellos crea nuevas tablas y grafica las variables solicitadas en el informe.
        Las etapas son:
            1) Carga de datasets y bibliotecas
            2) Gráfico correspondiente al punto i
            3) Gráfico correspondiente al punto ii
            4) Gráfico correspondiente al punto iii

    Ejecución:
        Ejecutar el script en consola generará los gráficos en la carpeta Gráficos/
'''


'''
Importar bibliotecas y cargar tablas.

'''

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Importamos los datasets que vamos a utilizar en este programa.
Migrantes = pd.read_csv("Tablas/Migrantes.csv")
Paises = pd.read_csv("Tablas/Paises.csv")
Regiones = pd.read_csv("Tablas/Regiones.csv")
Secciones = pd.read_csv("Tablas/Secciones.csv")
Sedes = pd.read_csv("Tablas/Sedes.csv")
Redes_Sociales = pd.read_csv("Tablas/Redes_Sociales.csv")

# Crear una conexión SQLite en memoria.
Connection = sqlite3.connect(':memory:')

# Cargar dfs en la base de datos SQLite.
Migrantes.to_sql('Migrantes', Connection, index=False, if_exists='replace')
Paises.to_sql('Paises', Connection, index=False, if_exists='replace')
Regiones.to_sql('Regiones', Connection, index=False, if_exists='replace')
Secciones.to_sql('Secciones', Connection, index=False, if_exists='replace')
Sedes.to_sql('Sedes', Connection, index=False, if_exists='replace')
Redes_Sociales.to_sql('Redes_Sociales', Connection, index=False, if_exists='replace')


'''
Punto i.

'''

Consulta_SQL = """
               SELECT R.nombre AS region,
                      COUNT(S.id_sede) AS cantidad_sedes
               FROM Paises AS P
               INNER JOIN Sedes AS S ON P.id = S.id_pais
               LEFT JOIN (
                            SELECT SC.id_sede, COUNT(SC.id_sede) AS cant_secciones
                            FROM Secciones AS SC
                            GROUP BY SC.id_sede
                         ) AS CS ON S.id_sede = CS.id_sede
               LEFT JOIN Regiones AS R ON P.id_region = R.id
               GROUP BY R.nombre
               ORDER BY cantidad_sedes DESC;
               
               """

# Armamos el DataFrame con los la cantidad de sedes, el promedio de secciones y el flujo migratorio neto por país.
Sedes_Por_Regiones = pd.read_sql_query(Consulta_SQL, Connection)

# Cambios en los textos para que queden más prolijo en el gráfico.
Sedes_Por_Regiones['region'] = Sedes_Por_Regiones['region'].apply(lambda x: x.title())
Sedes_Por_Regiones['region'] = Sedes_Por_Regiones['region'].apply(lambda x: x.replace(' Y ', ' y ') if ' Y ' in x else x)
Sedes_Por_Regiones['region'] = Sedes_Por_Regiones['region'].apply(lambda x: x.replace(' Del ', ' del ') if ' Del ' in x else x)

# Crear la figura y ajustar el tamaño.
Figure, Graphic_1 = plt.subplots(figsize=(10, 10))

# Ajustar la fuente global.
plt.rcParams['font.family'] = 'sans-serif'

# Dibujar el gráfico de barras.
Graphic_1.bar(Sedes_Por_Regiones['region'], Sedes_Por_Regiones['cantidad_sedes'])

# Título y etiquetas con mejor formato.
Graphic_1.set_xlabel('Regiones geográficas', fontsize=12, labelpad=10)
Graphic_1.set_ylabel('Cantidad de sedes', fontsize=12, labelpad=10)

# Establecer límite del eje Y dinámicamente.
Graphic_1.set_ylim(0, max(Sedes_Por_Regiones['cantidad_sedes']) + 10)

# Mostrar etiquetas de las barras con el valor exacto.
Graphic_1.bar_label(Graphic_1.containers[0], fontsize=10, padding=5)

# Rotar etiquetas del eje X.
Graphic_1.set_xticklabels(Sedes_Por_Regiones['region'], rotation=90, ha='right')

# Ajustar los márgenes para evitar que las etiquetas se corten.
plt.tight_layout()

# Guardar gráficos.
plt.savefig('Graficos/Punto i.png')

# Mostrar el gráfico.
#plt.show()


'''
Punto ii.

'''

# Recolectamos países que tienen sedes.
Paises_Con_Sedes = list(Sedes['id_pais'].unique())

# Filtramos df Migrantes con los países que tienen sedes.
Migrantes_Con_Sedes = Migrantes[Migrantes['id_pais'].isin(Paises_Con_Sedes)]

# Creamos la columna "Flujo Neto".
Migrantes_Con_Sedes.loc[:, 'Flujo_Neto'] = Migrantes_Con_Sedes.loc[:, 'inmigrantes'] - Migrantes_Con_Sedes.loc[:, 'emigrantes']

# Agrupar por país y calcular el promedio del flujo neto en los distintos años.
Migrantes_Con_Sedes = Migrantes_Con_Sedes.groupby('id_pais', as_index=False)['Flujo_Neto'].mean()

# Vinculamos la tabla con Paises y Regiones para hallar las Regiones.
Migrantes_Con_Sedes = Migrantes_Con_Sedes.merge(Paises, how='left', left_on='id_pais', right_on='id')
Migrantes_Con_Sedes = Migrantes_Con_Sedes.merge(Regiones, how='left', left_on='id_region', right_on='id')

# Filtramos columnas.
Migrantes_Con_Sedes = Migrantes_Con_Sedes[['nombre_y', 'id_pais', 'Flujo_Neto']]

# Cambiamos los nombres de las columnas.
Migrantes_Con_Sedes.rename(columns={'nombre_y': 'region'}, inplace=True)

# Damos formato a los nombres de las regiones para que se vean bien en el gráfico.
Migrantes_Con_Sedes['region'] = Migrantes_Con_Sedes['region'].apply(lambda x: x.title())
Migrantes_Con_Sedes['region'] = Migrantes_Con_Sedes['region'].apply(lambda x: x.replace(' Y ', ' y ') if ' Y ' in x else x)
Migrantes_Con_Sedes['region'] = Migrantes_Con_Sedes['region'].apply(lambda x: x.replace(' Del ', ' del ') if ' Del ' in x else x)

# Eliminar datos que joden.
Migrantes_Con_Sedes = Migrantes_Con_Sedes[Migrantes_Con_Sedes['id_pais'] != 'ITA']
Migrantes_Con_Sedes = Migrantes_Con_Sedes[Migrantes_Con_Sedes['id_pais'] != 'ESP']

# Función para eliminar outliers de un dataframe basándose en una columna.
def Eliminar_Outliers(df: pd.DataFrame, Columna: str) -> pd.DataFrame:

    # Calcular Q1 y Q3.
    Q1 = df[Columna].quantile(0.25)
    Q3 = df[Columna].quantile(0.75)
    IQR = Q3 - Q1  # Rango intercuartil.

    # Definir los límites para los outliers.
    Limite_Inferior = Q1 - 1.5 * IQR
    Limite_Superior = Q3 + 1.5 * IQR

    # Filtrar dataframe.
    df = df[(df[Columna] >= Limite_Inferior) & (df[Columna] <= Limite_Superior)]

    return df

# Definimos listas para separar los boxplots.
Regiones_Con_Mas_Flujo = ['América del Sur', 'América del Norte']
Regiones_Con_Menor_Flujo = [Region for Region in Migrantes_Con_Sedes['region'].unique() if Region not in Regiones_Con_Mas_Flujo]

# Crear DataFrames separados.
df_Regiones_Con_Mas_Flujo = Migrantes_Con_Sedes[Migrantes_Con_Sedes['region'].isin(Regiones_Con_Mas_Flujo)]
df_Regiones_Con_Menor_Flujo = Migrantes_Con_Sedes[Migrantes_Con_Sedes['region'].isin(Regiones_Con_Menor_Flujo)]

# Eliminamos outliers nuevamente en las de menor flujo para un mejor visionado.
df_Regiones_Con_Menor_Flujo = Eliminar_Outliers(df_Regiones_Con_Menor_Flujo, 'Flujo_Neto')

# Obtener las medianas para ordenar las regiones en el gráfico.
Medianas_Mayor_Flujo = df_Regiones_Con_Mas_Flujo.groupby('region')['Flujo_Neto'].median().sort_values().index.tolist()
Medianas_Menor_Flujo = df_Regiones_Con_Menor_Flujo.groupby('region')['Flujo_Neto'].median().sort_values().index.tolist()

# Creamos los gráficos: dos paneles.
Figure, Graficos = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

# Primer boxplot.
sns.boxplot(x='region', y='Flujo_Neto', data=df_Regiones_Con_Mas_Flujo, ax=Graficos[0], order=Medianas_Mayor_Flujo, palette='Set2')
Graficos[0].set_xlabel('Region', labelpad = 90)
Graficos[0].set_ylabel('Flujo migratorio neto')
Graficos[0].set_xticklabels(Graficos[0].get_xticklabels(), rotation=90, ha='right')  # Rotate x-axis labels
Graficos[0].grid(False) # Eliminar la cuadrícula
Graficos[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".") ))

# Segundo boxplot.
sns.boxplot(x='region', y='Flujo_Neto', data=df_Regiones_Con_Menor_Flujo, ax=Graficos[1], order=Medianas_Menor_Flujo, palette='Set1')
Graficos[1].set_xlabel('Region', labelpad = 50)
Graficos[1].set_ylabel('Flujo migratorio neto')
Graficos[1].set_xticklabels(Graficos[1].get_xticklabels(), rotation=90, ha='right')  # Rotate x-axis labels
Graficos[1].grid(False)  # Eliminar la cuadrícula
Graficos[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".") ))

# Ajustar los márgenes para evitar que las etiquetas se corten.
plt.tight_layout()

# Guardar gráficos.
plt.savefig('Graficos/Punto ii.png')

# Show the plots
#plt.show()


'''
Punto iii.

'''

Consulta_SQL = """
               SELECT M.id_pais, M.inmigrantes, COUNT(S.id_sede) AS cantidad_sedes
               FROM Migrantes AS M
               LEFT JOIN Paises AS P ON M.id_pais = P.id
               INNER JOIN Sedes AS S ON M.id_pais = S.id_pais
               WHERE anio = 2000
               GROUP BY M.id_pais
               ORDER BY M.inmigrantes DESC
               
               """

Flujo_Migratorio_2000 = pd.read_sql_query(Consulta_SQL, Connection)
Flujo_Migratorio_2000.head(10)
import numpy as np 

# Crear la figura y ajustar el tamaño.
Figure, Graphic_1 = plt.subplots(figsize=(10, 6))

plt.rcParams['font.family'] = 'sans-serif'

# Graficar los datos.
Graphic_1.plot('cantidad_sedes', 'inmigrantes', data=Flujo_Migratorio_2000, marker="o", linestyle='',
               markersize=10, label = '')

# Calcular la línea de tendencia (regresión lineal).
x = Flujo_Migratorio_2000['cantidad_sedes']
y = Flujo_Migratorio_2000['inmigrantes']
Slope, Intercept = np.polyfit(x, y, 1)
Trendline = Slope * x + Intercept

# Calcular R² (coeficiente de determinación).
Correlation_Matrix = np.corrcoef(x, y)
R_value = Correlation_Matrix[0, 1]**2  # R²

# Graficar la línea de tendencia.
Graphic_1.plot(x, Trendline, color='red', linestyle='--', label=f'R² = {R_value:.2f}')

# Etiquetas y título.
Graphic_1.set_ylabel('Inmigrantes', fontsize='medium', labelpad=15)
Graphic_1.set_xlabel('Cantidad de sedes', fontsize='medium', labelpad=15)

# Agregar separador de miles al eje Y.
Graphic_1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".") ))

# Ajustar el diseño para evitar recortes.
plt.tight_layout()

# Mostrar leyenda.
Graphic_1.legend()

# Guardar gráficos.
plt.savefig('Graficos/Punto iii.png')

# Mostrar el gráfico.
#plt.show()
