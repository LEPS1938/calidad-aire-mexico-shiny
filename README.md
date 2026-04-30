# ¿Dónde no conviene salir a correr?  
## Una historia visual sobre la calidad del aire en México

**Autor:** Luis Antonio López Abaunza
**Materia:** Visualización gráfica para IA  
**Universidad:** Universidad Iberoamericana León  
**Herramienta:** Shiny for Python  

---

## 1. Descripción del proyecto

Este proyecto presenta una narrativa visual interactiva sobre la calidad del aire en México a partir de datos reales de estaciones de monitoreo ambiental.

La pregunta central del proyecto es:

> **¿Dónde no conviene salir a correr?**

La idea es explorar cómo cambia la contaminación del aire dependiendo de la estación de monitoreo, el contaminante seleccionado, el mes del año y el día de la semana. El enfoque no busca reemplazar un sistema oficial de alerta ambiental, sino construir una historia visual clara y comprensible para observar patrones generales en los datos.

El proyecto fue desarrollado como una aplicación web con **Shiny for Python**, integrando texto narrativo, controles interactivos y visualizaciones con Plotly.

---

## 2. Pregunta de investigación

**¿Dónde no conviene salir a correr? Una historia visual sobre la calidad del aire en México.**

Esta pregunta se eligió porque permite comunicar un tema técnico de forma cercana. En lugar de presentar únicamente valores de contaminantes, se plantea una situación cotidiana: decidir en qué lugares y momentos podría ser menos recomendable hacer actividad física al aire libre.

La narrativa se organiza en tres preguntas secundarias:

1. **¿En qué zonas aparecen los valores más altos de contaminación?**  
   Se responde mediante un mapa interactivo de estaciones de monitoreo.

2. **¿Hay meses donde la contaminación sube?**  
   Se responde mediante una gráfica mensual del contaminante seleccionado.

3. **¿Hay días de la semana peores para salir a correr?**  
   Se responde mediante una gráfica de barras por día de la semana.

---

## 3. Fuente de datos

Los datos utilizados provienen del siguiente dataset público:

**Mexico Air Quality Dataset**  
Fuente: Kaggle  
URL: https://www.kaggle.com/datasets/elianaj/mexico-air-quality-dataset?resource=download  
Licencia: **CC0: Public Domain**  
Fecha de descarga: **27/04/2026**

Archivos utilizados:

- `stations_daily.csv`
- `stations_rsinaica.csv`
- `stations_hourly.csv`

Para la aplicación principal se trabajó con `stations_daily.csv` y `stations_rsinaica.csv`.

El archivo `stations_hourly.csv` también forma parte del dataset original, pero no se usa directamente en la aplicación porque tiene un tamaño aproximado de **546 MB**, lo cual puede afectar el rendimiento de Shiny y hacer más lento el despliegue en línea.

---

## 4. Descripción de los datos utilizados

### `stations_daily.csv`

Contiene mediciones diarias de contaminantes y variables ambientales por estación de monitoreo.

Algunas columnas relevantes son:

- `datetime`: fecha de medición.
- `station_id`: identificador de estación.
- `PM2.5`: partículas finas.
- `PM10`: partículas suspendidas.
- `O3`: ozono.
- `NO2`: dióxido de nitrógeno.
- `NOx`: óxidos de nitrógeno.
- `CO`: monóxido de carbono.
- otras variables ambientales como temperatura, humedad y radiación.

### `stations_rsinaica.csv`

Contiene información descriptiva de las estaciones de monitoreo.

Columnas relevantes:

- `station_id`: identificador de estación.
- `station_name`: nombre de la estación.
- `station_code`: código de la estación.
- `network_name`: red, ciudad o zona de monitoreo.
- `state_code`: código de estado.
- `municipio_code`: código de municipio.
- `lat`: latitud.
- `lon`: longitud.

Este archivo se usó para ubicar las estaciones en el mapa y agregar contexto geográfico a las mediciones.

### Exploración inicial

El archivo `notebooks/exploracion_inicial.ipynb` documenta el análisis exploratorio inicial del dataset. En él se revisan la estructura de los archivos, valores faltantes, rango de fechas, valores extremos, estaciones disponibles y diferencias entre el catálogo de estaciones y las estaciones con datos diarios.

## 5. Proceso de limpieza y transformación

El proceso de limpieza se encuentra en:

scripts/01_clean_data.py    

El script realiza los siguientes pasos:

1.-Carga los archivos originales desde data/raw/.
2.-Limpia los nombres de columnas para evitar errores por espacios ocultos.
3.-Convierte la columna datetime a formato de fecha.
4.-Selecciona las columnas necesarias del catálogo de estaciones.
5.-Convierte latitud y longitud a valores numéricos.
6.-Une las mediciones diarias con la información de las estaciones usando station_id.
7.-Crea variables temporales:
    año,
    mes,
    nombre del mes,
    día de la semana,
    nombre del día.
8.-Traduce meses y días.
9.-Convierte los contaminantes a formato numérico.
10.-Limpia valores extremos mediante percentil 99.9.
11.-Filtra registros sin fecha o sin coordenadas.
12.-Filtra coordenadas fuera del rango geográfico aproximado de México.
13.-Genera archivos procesados para la aplicación.

## 6. Limpieza de valores extremos

Durante la exploración de los datos se detectaron valores extremadamente altos en algunos contaminantes. Estos valores distorsionaban los promedios y hacían que las gráficas perdieran sentido visual.

Por ejemplo, algunos registros contenían valores de magnitud irreal para variables como PM2.5 o PM10.

Para evitar que esos datos dominaran las visualizaciones, se aplicó una limpieza basada en el percentil 99.9 de cada contaminante.

Esto significa que, para cada variable contaminante, se calculó el valor por debajo del cual se encuentra el 99.9% de las observaciones. Los valores superiores a ese límite fueron tratados como extremos y se convirtieron en valores faltantes.

Este criterio no busca definir si el aire es saludable o no según una norma ambiental. Su objetivo es únicamente mejorar la calidad del análisis exploratorio y evitar que errores de captura deformen los resultados.

También se eliminaron valores negativos, ya que las concentraciones ambientales no deberían ser menores que cero.

## 7. Nota metodológica sobre el rango de fechas

La documentación del dataset menciona que los datos compilados corresponden principalmente al periodo 2010–2021. Sin embargo, al revisar el archivo stations_daily.csv, se encontraron registros desde el año 2000.

En lugar de eliminar automáticamente esos registros, se conservaron para mantener la información disponible en el archivo original. Esta diferencia se documenta como parte de la revisión de calidad de datos.

Esta decisión permite que el análisis sea transparente: los datos se conservan, pero se reconoce que existe una diferencia entre la descripción general del dataset y el contenido del archivo diario.

## 8. Archivos generados

Después de ejecutar el script de limpieza, se generan los siguientes archivos en data/processed/:

air_quality_clean.csv: contiene el conjunto de datos limpio completo.
map_stations.csv: contiene promedios por estación y se usa para el mapa interactivo.
monthly_pollution.csv: contiene promedios mensuales por estación.
weekday_pollution.csv: contiene promedios por día de la semana.

air_quality_clean.csv
Contiene el conjunto de datos limpio completo.

map_stations.csv
Contiene promedios por estación. Se usa para el mapa interactivo.

monthly_pollution.csv
Contiene promedios mensuales por estación. Se usa para analizar patrones por mes.

weekday_pollution.csv
Contiene promedios por día de la semana. Se usa para comparar lunes, martes, miércoles, etc.

## 9. Visualizaciones implementadas

La aplicación incluye tres visualizaciones interactivas.

### 1. Mapa interactivo de estaciones

Pregunta que responde:
¿En qué zonas aparecen los valores más altos?
Cada punto representa una estación de monitoreo. El color y el tamaño del punto representan el promedio del contaminante seleccionado.

Canales visuales:
posición: latitud y longitud,
color: promedio del contaminante,
tamaño: promedio del contaminante,
hover: nombre de estación, código y zona de monitoreo.

Interactividad:
selector de contaminante,
filtro por ciudad o zona de monitoreo,
información al pasar el cursor sobre cada estación.


### 2. Gráfica mensual

Pregunta que responde:
¿Hay meses donde la contaminación sube?
Esta gráfica muestra el promedio mensual del contaminante seleccionado.

Canales visuales:
eje X: mes,
eje Y: promedio del contaminante,
puntos y línea: evolución mensual.

Interactividad:
cambia con el contaminante seleccionado,
cambia con la ciudad o zona seleccionada.


### 3. Gráfica por día de la semana

Pregunta que responde:
¿Hay días peores para salir a correr?
Esta gráfica compara el promedio del contaminante seleccionado entre lunes, martes, miércoles, jueves, viernes, sábado y domingo.

Canales visuales:
eje X: día de la semana,
eje Y: promedio del contaminante,
altura de barra: nivel promedio.

Interactividad:
cambia con el contaminante seleccionado,
cambia con la ciudad o zona seleccionada.


## 10. Estructura del repositorio
calidad-aire-mexico-shiny/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── stations_daily.csv
│   │   ├── stations_hourly.csv
│   │   ├── stations_rsinaica.csv
│   │   └── estados.json
│   │
│   └── processed/
│       ├── air_quality_clean.csv
│       ├── map_stations.csv
│       ├── monthly_pollution.csv
│       └── weekday_pollution.csv
│
├── scripts/
│   └── 01_clean_data.py
│
└── assets/
│
└── notebooks/
    └── exploracion_inicial.ipynb


## 11. Instalación y ejecución local
1. Clonar el repositorio
git clone https://github.com/LEPS1938/calidad-aire-mexico-shiny.git
cd calidad-aire-mexico-shiny
2. Crear entorno virtual
python -m venv .venv
3. Activar entorno virtual

En Windows PowerShell:

.\.venv\Scripts\activate
4. Instalar dependencias
pip install -r requirements.txt
5. Ejecutar limpieza de datos
python scripts/01_clean_data.py
6. Ejecutar la aplicación
shiny run --reload app.py

La aplicación se abrirá localmente en una dirección similar a:

http://127.0.0.1:8000


## 12. Dependencias principales

El proyecto utiliza:

pandas
plotly
shiny
shinywidgets
rsconnect-python

Estas dependencias se encuentran documentadas en:

requirements.txt


## 13. Despliegue

La aplicación fue desplegada usando shinyapps.io.

Link de la aplicación publicada:
https://testcito-visualizacion.shinyapps.io/correr-aire-mexico/


## 14. Limitaciones

Este proyecto tiene algunas limitaciones importantes:

- El archivo horario original es muy pesado, por lo que la aplicación utiliza datos diarios.
- Algunas estaciones aparecen en el catálogo, pero no tienen registros diarios disponibles.
- La documentación general del dataset menciona 2010–2021, aunque el archivo diario contiene registros desde 2000.
- La limpieza por percentil 99.9 elimina valores extremos, pero no reemplaza una validación ambiental oficial.
- Los resultados deben interpretarse como análisis exploratorio, no como diagnóstico oficial de calidad del aire.


## 15. Conclusión

La calidad del aire en México no se distribuye de forma uniforme. Los datos muestran que el nivel promedio de contaminantes cambia según la estación de monitoreo, la zona, el mes y el día de la semana.

La pregunta “¿dónde no conviene salir a correr?” permite convertir un conjunto de datos técnico en una narrativa visual más cercana. El análisis muestra que no basta con observar una ciudad completa: también importa el contaminante, la estación específica y el momento en que se mide.

Este proyecto demuestra cómo una aplicación interactiva puede ayudar a comunicar patrones ambientales de forma más clara para públicos no técnicos.


## 16. Créditos

Datos originales:

ELIANA KAI JUAREZ
Mexico Hourly Air Pollution (2010-2021)
Kaggle
https://www.kaggle.com/datasets/elianaj/mexico-air-quality-dataset?resource=download
Licencia: CC0 Public Domain

Herramientas utilizadas:

Python
Pandas
Plotly
Shiny for Python
Shinywidgets
GitHub
shinyapps.io