from pathlib import Path
import pandas as pd


# Ruta principal del proyecto.
# Permite que el script funcione aunque se ejecute desde otra carpeta.
BASE_DIR = Path(__file__).resolve().parents[1]

# Carpetas donde están los datos originales y donde se guardarán los datos procesados.
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# Archivos principales del proyecto.
# daily contiene las mediciones por día y stations contiene la información de las estaciones.
daily_path = RAW_DIR / "stations_daily.csv"
stations_path = RAW_DIR / "stations_rsinaica.csv"


# Lectura de archivos originales.
daily = pd.read_csv(daily_path)
stations = pd.read_csv(stations_path)


# Limpieza de nombres de columnas.
# Evita errores por espacios ocultos en los encabezados.
daily.columns = daily.columns.str.strip()
stations.columns = stations.columns.str.strip()


# Conversión de la fecha principal.
# Las fechas que no se puedan interpretar se convierten en valores vacíos.
daily["datetime"] = pd.to_datetime(
    daily["datetime"],
    errors="coerce",
    dayfirst=True
)


# Columnas necesarias del catálogo de estaciones.
# Se conservan los campos útiles para ubicar y describir cada estación.
station_cols = [
    "station_id",
    "station_name",
    "station_code",
    "network_name",
    "state_code",
    "municipio_code",
    "lat",
    "lon"
]

stations = stations[station_cols].copy()


# Conversión de coordenadas.
# Algunas coordenadas pueden venir como texto; aquí se transforman a número.
stations["lat"] = pd.to_numeric(stations["lat"], errors="coerce")
stations["lon"] = pd.to_numeric(stations["lon"], errors="coerce")


# Unión de mediciones con catálogo de estaciones.
# station_id es la llave común entre ambos archivos.
df = daily.merge(stations, on="station_id", how="left")


# Variables temporales para analizar patrones por año, mes y día de la semana.
df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.month
df["weekday"] = df["datetime"].dt.dayofweek
df["month_name"] = df["datetime"].dt.month_name()
df["weekday_name"] = df["datetime"].dt.day_name()


# Traducción de meses para que la app esté completamente en español.
month_map = {
    "January": "Enero",
    "February": "Febrero",
    "March": "Marzo",
    "April": "Abril",
    "May": "Mayo",
    "June": "Junio",
    "July": "Julio",
    "August": "Agosto",
    "September": "Septiembre",
    "October": "Octubre",
    "November": "Noviembre",
    "December": "Diciembre"
}

# Traducción de días de la semana.
weekday_map = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

df["month_name"] = df["month_name"].map(month_map)
df["weekday_name"] = df["weekday_name"].map(weekday_map)


# Contaminantes principales para la narrativa visual.
# Solo se usan columnas que sí existan en el archivo.
pollutants = ["PM2.5", "PM10", "O3", "NO2", "NOx", "CO"]
pollutants = [col for col in pollutants if col in df.columns]


# Conversión de contaminantes a formato numérico.
# Los valores no interpretables se convierten en NaN.
for col in pollutants:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# Limpieza de valores extremos por contaminante.
# Se eliminan valores negativos y valores superiores al percentil 99.9.
# Este criterio conserva casi todos los datos y reduce el efecto de errores de captura.
outlier_limits = {}
outlier_counts = {}

for col in pollutants:
    # Cantidad de valores disponibles antes de limpiar.
    before_count = df[col].notna().sum()

    # Las concentraciones ambientales no deberían ser negativas.
    df.loc[df[col] < 0, col] = pd.NA

    # Límite superior calculado con los propios datos.
    # El percentil 99.9 deja fuera el 0.1% más extremo de cada contaminante.
    upper_limit = df[col].quantile(0.999)

    # Conteo de valores por encima del límite.
    outliers = (df[col] > upper_limit).sum()

    # Se anulan solo los valores extremos, no la fila completa.
    df.loc[df[col] > upper_limit, col] = pd.NA

    # Se guardan los límites para documentarlos en la terminal.
    outlier_limits[col] = upper_limit
    outlier_counts[col] = {
        "valores_originales": before_count,
        "valores_extremos_eliminados": outliers
    }


# Filtrado mínimo para que las gráficas funcionen correctamente.
# Sin fecha o coordenadas no se puede ordenar ni ubicar una medición.
df = df.dropna(subset=["datetime", "lat", "lon"])


# Filtro geográfico básico para evitar coordenadas fuera de México.
# México se encuentra aproximadamente entre estas latitudes y longitudes.
df = df[
    (df["lat"].between(14, 33)) &
    (df["lon"].between(-119, -86))
]


# Archivo limpio completo.
df.to_csv(PROCESSED_DIR / "air_quality_clean.csv", index=False)


# Resumen por estación para el mapa.
# Cada punto del mapa representa una estación con el promedio de cada contaminante.
map_stations = (
    df.groupby(
        [
            "station_id",
            "station_name",
            "station_code",
            "network_name",
            "state_code",
            "lat",
            "lon"
        ],
        as_index=False
    )[pollutants]
    .mean()
)

map_stations.to_csv(PROCESSED_DIR / "map_stations.csv", index=False)


# Promedios mensuales para analizar temporadas del año.
monthly_pollution = (
    df.groupby(
        [
            "year",
            "month",
            "month_name",
            "station_id",
            "station_name",
            "network_name",
            "state_code"
        ],
        as_index=False
    )[pollutants]
    .mean()
)

monthly_pollution.to_csv(PROCESSED_DIR / "monthly_pollution.csv", index=False)


# Promedios por día de la semana para observar si hay días más problemáticos.
weekday_pollution = (
    df.groupby(
        [
            "weekday",
            "weekday_name",
            "station_id",
            "station_name",
            "network_name",
            "state_code"
        ],
        as_index=False
    )[pollutants]
    .mean()
)

weekday_pollution.to_csv(PROCESSED_DIR / "weekday_pollution.csv", index=False)


# Revisión rápida de salida.
print("Limpieza terminada.")
print(f"Filas limpias: {df.shape[0]:,}")
print(f"Columnas limpias: {df.shape[1]:,}")
print(f"Contaminantes usados: {pollutants}")
print(f"Estaciones con datos: {df['station_id'].nunique():,}")
print(f"Rango de fechas: {df['datetime'].min()} a {df['datetime'].max()}")

print("\nLímites superiores usados para valores extremos:")
for col, limit in outlier_limits.items():
    removed = outlier_counts[col]["valores_extremos_eliminados"]
    total = outlier_counts[col]["valores_originales"]
    print(f"{col}: límite={limit:.6f} | extremos eliminados={removed:,} de {total:,}")

print("\nArchivos generados en data/processed:")
print("- air_quality_clean.csv")
print("- map_stations.csv")
print("- monthly_pollution.csv")
print("- weekday_pollution.csv")