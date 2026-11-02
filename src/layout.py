from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

def create_kpi_cards(df: pd.DataFrame):
    total_muertes = len(df)
    masculino = len(df[df["SEXO_TXT"] == "Masculino"])
    femenino = len(df[df["SEXO_TXT"] == "Femenino"])
    pct_masc = (masculino / total_muertes * 100) if total_muertes else 0
    pct_fem = (femenino / total_muertes * 100) if total_muertes else 0

    top_depto = df["DEPARTAMENTO"].value_counts().index[0] if not df["DEPARTAMENTO"].dropna().empty else "N/A"
    top_depto_val = df["DEPARTAMENTO"].value_counts().iloc[0] if not df["DEPARTAMENTO"].dropna().empty else 0

    card_style = {
        "backgroundColor": "#1E293B",
        "border": "1px solid #334155",
        "borderRadius": "10px",
        "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.3)"
    }

    return dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Total Defunciones 2019", className="text-muted mb-1 text-uppercase small font-weight-bold"),
                    html.H3(f"{total_muertes:,d}", className="text-info font-weight-bold mb-0"),
                    html.Small("100% de registros analizados", className="text-secondary")
                ]),
                style=card_style, className="mb-3"
            ), md=3, sm=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Mortalidad Masculina", className="text-muted mb-1 text-uppercase small font-weight-bold"),
                    html.H3(f"{masculino:,d}", className="text-primary font-weight-bold mb-0"),
                    html.Small(f"{pct_masc:.1f}% del total nacional", className="text-secondary")
                ]),
                style=card_style, className="mb-3"
            ), md=3, sm=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Mortalidad Femenina", className="text-muted mb-1 text-uppercase small font-weight-bold"),
                    html.H3(f"{femenino:,d}", className="text-danger font-weight-bold mb-0"),
                    html.Small(f"{pct_fem:.1f}% del total nacional", className="text-secondary")
                ]),
                style=card_style, className="mb-3"
            ), md=3, sm=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Departamento Mayor Mortalidad", className="text-muted mb-1 text-uppercase small font-weight-bold"),
                    html.H3(f"{top_depto}", className="text-warning font-weight-bold mb-0", style={"fontSize": "1.4rem"}),
                    html.Small(f"{top_depto_val:,d} casos registrados", className="text-secondary")
                ]),
                style=card_style, className="mb-3"
            ), md=3, sm=6
        ),
    ], className="mb-3")

def create_layout(df_total: pd.DataFrame, df_causas: pd.DataFrame, choices: list):
    from figures import (
        fig_mapa, fig_lineas_mes, fig_ciudades_violentas,
        fig_menor_mortalidad, fig_tabla_causas, fig_sexo_departamento,
        fig_ciclo_vida
    )

    deptos = sorted([str(d) for d in df_total["DEPARTAMENTO"].dropna().unique()])
    dept_options = [{"label": "Todos los Departamentos", "value": "ALL"}] + [{"label": d, "value": d} for d in deptos]

    mes_options = [
        {"label": "Todos los Meses", "value": "ALL"},
        {"label": "Enero", "value": "Ene"}, {"label": "Febrero", "value": "Feb"},
        {"label": "Marzo", "value": "Mar"}, {"label": "Abril", "value": "Abr"},
        {"label": "Mayo", "value": "May"}, {"label": "Junio", "value": "Jun"},
        {"label": "Julio", "value": "Jul"}, {"label": "Agosto", "value": "Ago"},
        {"label": "Septiembre", "value": "Sep"}, {"label": "Octubre", "value": "Oct"},
        {"label": "Noviembre", "value": "Nov"}, {"label": "Diciembre", "value": "Dic"}
    ]

    return dbc.Container([
        # ENCABEZADO
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1(
                        "Análisis de Mortalidad en Colombia — 2019",
                        className="display-6 font-weight-bold text-white mb-1"
                    ),
                    html.P(
                        "Dashboard dinámico e interactivo de Estadísticas Vitales (EEVV) del DANE con Plotly y Dash",
                        className="text-info lead mb-0",
                        style={"fontSize": "1.05rem"}
                    )
                ], className="py-2")
            ], md=8),
            dbc.Col([
                html.Div([
                    dbc.Button(
                        [html.I(className="bi bi-github me-2"), "Repositorio GitHub"],
                        id="btn-github",
                        href="https://github.com/dsgonzalezb/mortalidad-colombia-2019",
                        target="_blank",
                        color="outline-info",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Badge("DANE 2019", color="primary", className="p-2 me-1"),
                    dbc.Badge("CIE-10", color="secondary", className="p-2")
                ], className="d-flex justify-content-md-end align-items-center h-100 mt-2 mt-md-0")
            ], md=4)
        ], className="border-bottom border-secondary pb-3 mb-3"),

        # TARJETAS DE INDICADORES (KPI)
        html.Div(id="kpi-container", children=create_kpi_cards(df_total)),

        # BARRA DE FILTROS INTERACTIVOS
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("📍 Departamento:", className="text-light small font-weight-bold mb-1"),
                        dcc.Dropdown(
                            id="filtro-depto",
                            options=dept_options,
                            value="ALL",
                            clearable=False,
                            className="text-dark",
                            style={"color": "#0F172A"}
                        )
                    ], md=4, sm=12, className="mb-2 mb-md-0"),
                    dbc.Col([
                        html.Label("⚧️ Sexo:", className="text-light small font-weight-bold mb-1"),
                        dcc.Dropdown(
                            id="filtro-sexo",
                            options=[
                                {"label": "Todos los Sexos", "value": "ALL"},
                                {"label": "Masculino", "value": "Masculino"},
                                {"label": "Femenino", "value": "Femenino"},
                                {"label": "Indeterminado", "value": "Indeterminado"}
                            ],
                            value="ALL",
                            clearable=False,
                            className="text-dark",
                            style={"color": "#0F172A"}
                        )
                    ], md=4, sm=12, className="mb-2 mb-md-0"),
                    dbc.Col([
                        html.Label("📅 Mes:", className="text-light small font-weight-bold mb-1"),
                        dcc.Dropdown(
                            id="filtro-mes",
                            options=mes_options,
                            value="ALL",
                            clearable=False,
                            className="text-dark",
                            style={"color": "#0F172A"}
                        )
                    ], md=4, sm=12)
                ])
            ]),
            style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"},
            className="mb-4"
        ),

        # PESTAÑAS PRINCIPALES DEL DASHBOARD
        dbc.Tabs([
            # PESTAÑA 1: GEOGRAFÍA Y GÉNERO
            dbc.Tab(
                label="🗺️ Geografía y Género",
                tab_id="tab-geo",
                label_style={"color": "#94A3B8"},
                active_label_style={"color": "#38BDF8", "fontWeight": "bold"},
                children=[
                    html.Div(className="pt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="graph-mapa",
                                        figure=fig_mapa(df_total),
                                        style={"height": "560px"}
                                    )
                                ]),
                                style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"}
                            )
                        ], lg=6, className="mb-3"),
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="graph-sexo-depto",
                                        figure=fig_sexo_departamento(df_total),
                                        style={"height": "560px"}
                                    )
                                ]),
                                style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"}
                            )
                        ], lg=6, className="mb-3")
                    ])
                ]
            ),

            # PESTAÑA 2: TENDENCIAS Y CICLO DE VIDA
            dbc.Tab(
                label="📈 Temporalidad y Ciclo de Vida",
                tab_id="tab-tiempo",
                label_style={"color": "#94A3B8"},
                active_label_style={"color": "#38BDF8", "fontWeight": "bold"},
                children=[
                    html.Div(className="pt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="graph-lineas-mes",
                                        figure=fig_lineas_mes(df_total),
                                        style={"height": "480px"}
                                    )
                                ]),
                                style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"}
                            )
                        ], lg=6, className="mb-3"),
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="graph-ciclo-vida",
                                        figure=fig_ciclo_vida(df_total, choices),
                                        style={"height": "480px"}
                                    )
                                ]),
                                style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"}
                            )
                        ], lg=6, className="mb-3")
                    ])
                ]
            ),

            # PESTAÑA 3: VIOLENCIA Y MENOR MORTALIDAD
            dbc.Tab(
                label="⚠️ Violencia y Extremos",
                tab_id="tab-violencia",
                label_style={"color": "#94A3B8"},
                active_label_style={"color": "#38BDF8", "fontWeight": "bold"},
                children=[
                    html.Div(className="pt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="graph-violencia",
                                        figure=fig_ciudades_violentas(df_total),
                                        style={"height": "480px"}
                                    )
                                ]),
                                style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"}
                            )
                        ], lg=6, className="mb-3"),
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="graph-menor-mortalidad",
                                        figure=fig_menor_mortalidad(df_total),
                                        style={"height": "480px"}
                                    )
                                ]),
                                style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"}
                            )
                        ], lg=6, className="mb-3")
                    ])
                ]
            ),

            # PESTAÑA 4: CAUSAS DE MUERTE
            dbc.Tab(
                label="📋 Principales Causas CIE-10",
                tab_id="tab-causas",
                label_style={"color": "#94A3B8"},
                active_label_style={"color": "#38BDF8", "fontWeight": "bold"},
                children=[
                    html.Div(className="pt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="graph-tabla-causas",
                                        figure=fig_tabla_causas(df_total, df_causas),
                                        style={"height": "480px"}
                                    )
                                ]),
                                style={"backgroundColor": "#1E293B", "border": "1px solid #334155", "borderRadius": "10px"}
                            )
                        ], lg=12, className="mb-3")
                    ])
                ]
            ),
        ], style={"borderBottom": "1px solid #334155"}),

        # FOOTER
        html.Footer([
            dbc.Row([
                dbc.Col([
                    html.P([
                        "Fuente: ",
                        html.A(
                            "DANE - Estadísticas Vitales (EEVV) 2019",
                            href="https://microdatos.dane.gov.co/index.php/catalog/696",
                            target="_blank",
                            className="text-info text-decoration-none"
                        ),
                        " | Codificación CIE-10 y DIVIPOLA | Aplicación desarrollada en Python con Dash y Plotly."
                    ], className="text-secondary small mb-0")
                ], md=12, className="text-center py-4 border-top border-secondary mt-4")
            ])
        ])

    ], fluid=True, style={"backgroundColor": "#0F172A", "minHeight": "100vh", "padding": "1.5rem 2rem"})

