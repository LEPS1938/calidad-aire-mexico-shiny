import pandas as pd
import plotly.express as px

from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_widget


# Carga de datos ya procesados.
# Se usan archivos filtrados para que la aplicación cargue más rápido.
map_stations = pd.read_csv("data/processed/map_stations.csv")
monthly_pollution = pd.read_csv("data/processed/monthly_pollution.csv")
weekday_pollution = pd.read_csv("data/processed/weekday_pollution.csv")


# Contaminantes disponibles para el análisis.
# Se filtran contra las columnas reales para evitar errores si falta alguno.
pollutants = ["PM2.5", "PM10", "O3", "NO2", "NOx", "CO"]
pollutants = [col for col in pollutants if col in map_stations.columns]


# Orden natural de los días para que no aparezcan alfabéticamente.
weekday_order = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo"
]

def empty_figure(message):
    """Figura vacía para selecciones sin datos disponibles."""
    fig = px.scatter()
    fig.update_layout(
        title=message,
        height=420,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 18}
            }
        ]
    )
    return fig

# Interfaz de la aplicación.
# La estructura se plantea como una narrativa.
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style(
            """
            body {
                max-width: 1200px;
                margin: auto;
                padding: 20px;
                font-family: Arial, sans-serif;
            }

            .hero {
                background: #f3f7f5;
                padding: 28px;
                border-radius: 18px;
                margin-bottom: 24px;
            }

            .section {
                margin-top: 36px;
                margin-bottom: 28px;
            }

            .note {
                background: #fff8e6;
                padding: 16px;
                border-left: 5px solid #e0a800;
                border-radius: 8px;
                margin-top: 14px;
            }

            h1 {
                font-weight: 800;
            }

            h2 {
                margin-top: 10px;
            }
            """
        )
    ),

    ui.div(
        {"class": "hero"},
        ui.h1("¿Dónde no conviene salir a correr?"),
        ui.h3("Una historia visual sobre la calidad del aire en México"),
        ui.p(
            "La contaminación del aire no se distribuye igual en todo el país. "
            "Algunas estaciones registran concentraciones más altas, algunos meses son más críticos "
            "y ciertos días de la semana pueden mostrar patrones distintos. "
            "Esta aplicación explora esos cambios usando datos reales de estaciones de monitoreo en México."
        ),
        ui.p(
            "Fuente: Mexico Hourly Air Pollution (2010-2021), Kaggle. "
            "Licencia: CC0 Public Domain."
        )
    ),

    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Controles"),
            ui.input_select(
                "pollutant",
                "Contaminante:",
                choices=pollutants,
                selected="PM2.5"
            ),
            ui.input_select(
                "zone",
                "Ciudad o zona de monitoreo:",
                choices=["Todos"] + sorted(map_stations["network_name"].dropna().unique().tolist()),
                selected="Todos"
            ),
            ui.hr(),
            ui.p(
                "Usa los controles para cambiar el contaminante y filtrar las estaciones por ciudad o zona de monitoreo."
            )
        ),

        ui.div(
            {"class": "section"},
            ui.h2("1. Primero: ¿en qué zonas aparecen los valores más altos?"),
            ui.p(
                "El mapa muestra el promedio registrado por estación. "
                "Cada punto representa una estación de monitoreo; el color indica el nivel promedio "
                "del contaminante seleccionado. Esta vista permite detectar rápidamente zonas donde "
                "correr al aire libre podría ser menos recomendable."
            ),
            output_widget("map_plot"),
            ui.div(
                {"class": "note"},
                ui.output_text("map_comment")
            )
        ),

        ui.div(
            {"class": "section"},
            ui.h2("2. Después: ¿hay meses donde la contaminación sube?"),
            ui.p(
                "La siguiente gráfica resume el comportamiento mensual del contaminante. "
                "La idea es observar si el problema se mantiene estable o si existen temporadas "
                "con incrementos claros."
            ),
            output_widget("monthly_plot")
        ),

        ui.div(
            {"class": "section"},
            ui.h2("3. Finalmente: ¿hay días peores para salir a correr?"),
            ui.p(
                "Esta gráfica compara el promedio por día de la semana. "
                "No busca demostrar causalidad, sino detectar si existen diferencias visibles "
                "entre lunes, fines de semana u otros días."
            ),
            output_widget("weekday_plot")
        ),

        ui.div(
            {"class": "section"},
            ui.h2("Conclusión"),
            ui.p(
                "Los datos muestran que la calidad del aire cambia según la estación, el contaminante y el momento del año. "
                "Para decidir dónde no conviene salir a correr no basta observar una ciudad completa: es necesario revisar "
                "la estación específica, el contaminante seleccionado y el patrón temporal. Esta diferencia entre zonas confirma "
                "que la exposición al aire contaminado no es uniforme en México."
            )
        )
    )
)


def server(input, output, session):

    @reactive.calc
    def filtered_map_data():
        """Datos del mapa filtrados por ciudad o zona."""
        pollutant = input.pollutant()
        zone = input.zone()

        data = map_stations.dropna(subset=[pollutant, "lat", "lon"]).copy()

        if zone != "Todos":
            data = data[data["network_name"] == zone]

        return data

    @reactive.calc
    def filtered_monthly_data():
        """Datos mensuales filtrados por ciudad o zona."""
        pollutant = input.pollutant()
        zone = input.zone()

        data = monthly_pollution.dropna(subset=[pollutant]).copy()

        if zone != "Todos":
            data = data[data["network_name"] == zone]

        return data

    @reactive.calc
    def filtered_weekday_data():
        """Datos por día filtrados por ciudad o zona"""
        pollutant = input.pollutant()
        zone = input.zone()

        data = weekday_pollution.dropna(subset=[pollutant]).copy()

        if zone != "Todos":
            data = data[data["network_name"] == zone]

        return data

    @render_widget
    def map_plot():
        pollutant = input.pollutant()
        data = filtered_map_data()

        if data.empty:
            return empty_figure("No hay datos disponibles para esta selección.")

        fig = px.scatter_map(
            data,
            lat="lat",
            lon="lon",
            color=pollutant,
            size=pollutant,
            size_max=18,
            hover_name="station_name",
            hover_data={
                "station_code": True,
                "network_name": True,
                pollutant: ":.3f",
                "lat": False,
                "lon": False
            },
            zoom=4,
            height=620,
            title=f"Promedio de {pollutant} por estación de monitoreo",
            color_continuous_scale="Plasma"
        )

        fig.update_layout(
            map_style="open-street-map",
            margin=dict(l=0, r=0, t=50, b=0)
        )

        return fig

    @render_widget
    def monthly_plot():
        pollutant = input.pollutant()
        data = filtered_monthly_data()

        if data.empty:
            return empty_figure("No hay datos mensuales para esta selección.")

        monthly_avg = (
            data.groupby(["month", "month_name"], as_index=False)[pollutant]
            .mean()
            .sort_values("month")
        )

        fig = px.line(
            monthly_avg,
            x="month_name",
            y=pollutant,
            markers=True,
            title=f"Promedio mensual de {pollutant}",
            labels={
                "month_name": "Mes",
                pollutant: f"Promedio de {pollutant}"
            }
        )

        fig.update_layout(
            xaxis_title="Mes",
            yaxis_title=f"Promedio de {pollutant}",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig

    @render_widget
    def weekday_plot():
        pollutant = input.pollutant()
        data = filtered_weekday_data()

        if data.empty:
            return empty_figure("No hay datos por día de la semana para esta selección.")

        weekday_avg = (
            data.groupby(["weekday", "weekday_name"], as_index=False)[pollutant]
            .mean()
            .sort_values("weekday")
        )

        fig = px.bar(
            weekday_avg,
            x="weekday_name",
            y=pollutant,
            title=f"Promedio de {pollutant} por día de la semana",
            labels={
                "weekday_name": "Día de la semana",
                pollutant: f"Promedio de {pollutant}"
            },
            category_orders={"weekday_name": weekday_order}
        )

        fig.update_layout(
            xaxis_title="Día de la semana",
            yaxis_title=f"Promedio de {pollutant}",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig

    @render.text
    def map_comment():
        pollutant = input.pollutant()
        data = filtered_map_data()

        if data.empty:
            return "No hay datos disponibles para esta selección."

        top_station = data.sort_values(pollutant, ascending=False).iloc[0]

        return (
            f"Para {pollutant}, la estación con el promedio más alto en esta selección es "
            f"{top_station['station_name']} en ({top_station['network_name']}), "
            f"con un valor promedio de {top_station[pollutant]:.3f}."
        )


app = App(app_ui, server)