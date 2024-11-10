*** Este repositorio contiene el código necesario para ejecutar un análisis completo sobre clasificación de dígitos manuscritos utilizando los algoritmos 
K-Nearest Neighbors (KNN) y Árbol de Decisión. El código está estructurado en diferentes archivos que implementan las etapas del trabajo.
Se detallan las instrucciones para ejecutar el código correctamente. ***


*** BIBLIOTECAS REQUERIDAS ***.
Este proyecto requiere las siguientes bibliotecas de Python para poder ejecutarse sin problemas. Hay que asegurarse de tenerlas instaladas en el entorno. 
Si no se las tiene, se puedes instalar cada utilizando el gestor de paquetes pip.

- pandas: manipulación y análisis de datos.
- numpy: operaciones matemáticas y manejo de matrices.
- matplotlib: gráficos y visualizaciones.
- PIL: abrir, manipular y guardar imágenes.
- scikit-learn: Entrenar y evaluar los modelos de clasificación (KNN y Árbol de Decisión).
- seaborn: gráficos avanzados, especialmente matrices de confusión y visualizaciones estadísticas.


*** INSTRUCCIONES PARA LA INSTALACIÓN DE BIBLIOTECAS ***
Se pueden instalar todas las bibliotecas necesarias utilizando el siguiente comando de pip:

pip install pandas numpy matplotlib pillow scikit-learn seaborn


*** ESTRUCTURA DEL PROYECTO ***
El proyecto se organiza en los siguientes archivos y carpetas:

- Auxiliares/Graficos.py: contiene funciones para generar gráficos y visualizaciones relacionadas con el análisis exploratorio.
- Auxiliares/ClasificacionBinaria.py: implementa las funciones necesarias para realizar la clasificación binaria utilizando el modelo KNN.
- Auxiliares/ClasificacionMulticlase.py: implementa las funciones necesarias para realizar la clasificación multiclase utilizando el modelo de Árbol de Decisión.
- tmnist_serendipicos.py: el archivo principal que ejecuta el flujo completo del trabajo, incluyendo la carga del dataset, la generación de gráficos 
y el entrenamiento y prueba de los modelos.


*** INSTRUCCIONES PARA LA EJECUCIÓN ***
Para ejecutar el código y realizar todo el análisis, hay que seguir estos pasos:

1. Colocar el archivo dataset (TMNIST_Data.csv) en la misma carpeta donde se encuentran el programa tmnist_serendipicos.py.
2. Ejecutar el archivo principal tmnist_serendipicos.py, que es el que orquesta todo el flujo de trabajo, cargando el dataset, generando las 
visualizaciones y entrenando los modelos. Si se está utilizando un entorno de desarrollo como VSCode o Jupyter Notebook, se puede ejecutar el script desde ahí. 
Si se prefiere usar la terminal, se puede ejecutar el archivo de la siguiente manera:

python tmnist_serendipicos.py

3. Verificar los resultados. Una vez que el script se haya ejecutado correctamente, los gráficos generados se guardan en una carpeta denominada Graficos/. 
Por otro lado, los resultados de la clasificación binaria y multiclase se mostrarán por consola.


*** DESCRIPCIÓN DE LAS ETAPAS ***
El flujo de trabajo se divide en las siguientes etapas:

1. Carga del Dataset TMNIST.
2. Se generan gráficos de análisis exploratorio que permiten visualizar las características y distribución de los datos.
3. Se realiza una clasificación binaria para predecir si una imagen corresponde al dígito "0" o al dígito "1" utilizando el algoritmo KNN.
4. Se entrena un modelo de Árbol de Decisión para predecir uno de los 10 dígitos posibles en el dataset.


*** PROBLEMAS FRECUENTES ***
Si se encuentra algún problema durante la ejecución, verificar lo siguiente:

- Asegurarse de que el archivo TMNIST_Data.csv esté en la misma carpeta que el script tmnist_serendipicos.py.
- Verificar que todas las bibliotecas necesarias estén correctamente instaladas utilizando el comando de instalación mencionado anteriormente.
