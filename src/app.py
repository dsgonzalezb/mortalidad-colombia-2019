import os
import sys

# Agregar carpeta src al path de importación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import dash
from dash import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

from load_data import load_data
from layout import create_layout, create_kpi_cards
from figures import (
    fig_mapa, fig_lineas_mes, fig_ciudades_violentas,
    fig_menor_mortalidad, fig_tabla_causas, fig_sexo_departamento,
    fig_ciclo_vida
)

# Carga de datos inicial
df_mortalidad_total, df_causas, choices = load_data()

# Inicialización de la aplicación Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css"
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

app.title = "Mortalidad Colombia 2019 | Dashboard Dinámico Dash"

# Instancia del servidor WSGI expuesta para Gunicorn y plataformas PaaS (Render, Railway, etc.)
server = app.server

# Definición del Layout
app.layout = create_layout(df_mortalidad_total, df_causas, choices)

# Callback dinámico para interactividad con los filtros
@app.callback(
    [
        Output("kpi-container", "children"),
        Output("graph-mapa", "figure"),
        Output("graph-sexo-depto", "figure"),
        Output("graph-lineas-mes", "figure"),
        Output("graph-ciclo-vida", "figure"),
        Output("graph-violencia", "figure"),
        Output("graph-menor-mortalidad", "figure"),
        Output("graph-tabla-causas", "figure"),
    ],
    [
        Input("filtro-depto", "value"),
        Input("filtro-sexo", "value"),
        Input("filtro-mes", "value")
    ]
)
def update_dashboard(depto_sel, sexo_sel, mes_sel):
    filtered_df = df_mortalidad_total

    if depto_sel and depto_sel != "ALL":
        filtered_df = filtered_df[filtered_df["DEPARTAMENTO"] == depto_sel]

    if sexo_sel and sexo_sel != "ALL":
        filtered_df = filtered_df[filtered_df["SEXO_TXT"] == sexo_sel]

    if mes_sel and mes_sel != "ALL":
        filtered_df = filtered_df[filtered_df["MES_NOMBRE"] == mes_sel]

    # Si el filtro no retorna registros, evitar errores retornando con dataset completo o vacío seguro
    if filtered_df.empty:
        filtered_df = df_mortalidad_total.head(1)

    kpis = create_kpi_cards(filtered_df)
    f_mapa = fig_mapa(filtered_df)
    f_sexo_depto = fig_sexo_departamento(filtered_df)
    f_lineas = fig_lineas_mes(filtered_df)
    f_ciclo = fig_ciclo_vida(filtered_df, choices)
    f_violencia = fig_ciudades_violentas(filtered_df)
    f_menor = fig_menor_mortalidad(filtered_df)
    f_tabla = fig_tabla_causas(filtered_df, df_causas)

    return kpis, f_mapa, f_sexo_depto, f_lineas, f_ciclo, f_violencia, f_menor, f_tabla

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)

