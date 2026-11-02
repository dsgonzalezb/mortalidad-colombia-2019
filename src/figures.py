import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de tema visual
THEME_DARK = dict(
    paper_bgcolor='#0F172A',
    plot_bgcolor='#1E293B',
    font=dict(color='#E2E8F0', family='Segoe UI, Arial, sans-serif'),
    legend=dict(bgcolor='#1E293B', bordercolor='#334155', borderwidth=1, font=dict(color='#CBD5E1'))
)

GEOJSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "colombia_departamentos.geojson")

def get_colombia_geojson():
    if os.path.exists(GEOJSON_PATH):
        try:
            with open(GEOJSON_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

# 1. Mapa de distribución de muertes por departamento (Mapa Coroplético con límites departamentales)
def fig_mapa(df: pd.DataFrame):
    df_dep = df.dropna(subset=['COD_DEPARTAMENTO', 'DEPARTAMENTO'])
    conteo = df_dep.groupby(['COD_DEPARTAMENTO', 'DEPARTAMENTO']).size().reset_index(name='NUM_MUERTES')
    conteo['COD_DPTO_STR'] = conteo['COD_DEPARTAMENTO'].astype(int).apply(lambda x: f"{x:02d}")
    
    geo = get_colombia_geojson()

    if geo is not None:
        # Mapa Coroplético con división de polígonos por departamento
        if hasattr(px, 'choropleth_map'):
            fig = px.choropleth_map(
                conteo,
                geojson=geo,
                locations='COD_DPTO_STR',
                featureidkey='properties.DPTO',
                color='NUM_MUERTES',
                hover_name='DEPARTAMENTO',
                hover_data={'COD_DPTO_STR': False, 'NUM_MUERTES': ':,d'},
                color_continuous_scale='Reds',
                zoom=4.5,
                center={"lat": 4.5709, "lon": -74.2973},
                map_style='carto-positron',
                title='<b>Distribución Total de Muertes por Departamento (2019)</b>',
                labels={'NUM_MUERTES': 'Defunciones'}
            )
        else:
            fig = px.choropleth_mapbox(
                conteo,
                geojson=geo,
                locations='COD_DPTO_STR',
                featureidkey='properties.DPTO',
                color='NUM_MUERTES',
                hover_name='DEPARTAMENTO',
                hover_data={'COD_DPTO_STR': False, 'NUM_MUERTES': ':,d'},
                color_continuous_scale='Reds',
                zoom=4.5,
                center={"lat": 4.5709, "lon": -74.2973},
                mapbox_style='carto-positron',
                title='<b>Distribución Total de Muertes por Departamento (2019)</b>',
                labels={'NUM_MUERTES': 'Defunciones'}
            )
    else:
        # Fallback a scatter map con burbujas
        df_geo_conteo = df.dropna(subset=['LATITUD', 'LONGITUD', 'DEPARTAMENTO']).groupby(['DEPARTAMENTO', 'LATITUD', 'LONGITUD']).size().reset_index(name='NUM_MUERTES')
        if hasattr(px, 'scatter_map'):
            fig = px.scatter_map(
                df_geo_conteo,
                lat='LATITUD', lon='LONGITUD',
                size='NUM_MUERTES', color='NUM_MUERTES',
                hover_name='DEPARTAMENTO',
                color_continuous_scale='Reds',
                size_max=45, zoom=4.5,
                center={"lat": 4.5709, "lon": -74.2973},
                map_style='carto-positron',
                title='<b>Distribución Total de Muertes por Departamento (2019)</b>',
                labels={'NUM_MUERTES': 'Defunciones'}
            )
        else:
            fig = px.scatter_mapbox(
                df_geo_conteo,
                lat='LATITUD', lon='LONGITUD',
                size='NUM_MUERTES', color='NUM_MUERTES',
                hover_name='DEPARTAMENTO',
                color_continuous_scale='Reds',
                size_max=45, zoom=4.5,
                center={"lat": 4.5709, "lon": -74.2973},
                mapbox_style='carto-positron',
                title='<b>Distribución Total de Muertes por Departamento (2019)</b>',
                labels={'NUM_MUERTES': 'Defunciones'}
            )

    fig.update_layout(
        **THEME_DARK,
        margin=dict(l=10, r=10, t=50, b=10),
        coloraxis_colorbar=dict(title="Muertes", tickfont=dict(color='#CBD5E1'))
    )
    return fig

# 2. Gráfico de líneas de muertes por mes
def fig_lineas_mes(df: pd.DataFrame):
    orden_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    conteo = df.groupby('MES_NOMBRE').size().reindex(orden_meses, fill_value=0).reset_index(name='NUM_MUERTES')
    conteo.columns = ['MES', 'NUM_MUERTES']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=conteo['MES'],
        y=conteo['NUM_MUERTES'],
        text=[f"{v:,d}" for v in conteo['NUM_MUERTES']],
        mode='lines+markers+text',
        textposition='top center',
        textfont=dict(size=11, color='#38BDF8'),
        marker=dict(size=8, color='#38BDF8', line=dict(color='#FFFFFF', width=1.5)),
        line=dict(color='#0284C7', width=3, shape='spline'),
        hovertemplate='<b>Mes:</b> %{x}<br><b>Muertes:</b> %{y:,d}<extra></extra>'
    ))
    fig.update_layout(
        title='<b>Total de Muertes por Mes en Colombia (2019)</b>',
        xaxis_title="Mes del año",
        yaxis_title="Total de defunciones",
        **THEME_DARK,
        margin=dict(l=40, r=20, t=50, b=40)
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155', tickformat=":,d")
    return fig

# 3. Gráfico de barras: Top 5 ciudades más violentas
def fig_ciudades_violentas(df: pd.DataFrame):
    codigos_violencia = ['X93', 'X94', 'X95']
    df_armas = df[df['COD_MUERTE'].astype(str).str.startswith(('X93', 'X94', 'X95'))]
        
    conteo = df_armas.groupby('MUNICIPIO').size().reset_index(name='HOMICIDIOS')
    top5 = conteo.sort_values('HOMICIDIOS', ascending=False).head(5)
    
    fig = px.bar(
        top5,
        x='MUNICIPIO',
        y='HOMICIDIOS',
        text='HOMICIDIOS',
        color='HOMICIDIOS',
        color_continuous_scale='Reds',
        title='<b>Top 5 Ciudades con Mayor Número de Homicidios por Arma de Fuego (X93-X95)</b>',
        labels={'MUNICIPIO': 'Ciudad / Municipio', 'HOMICIDIOS': 'Homicidios'}
    )
    fig.update_traces(
        texttemplate='%{text:,d}',
        textposition='outside',
        marker_line_color='#7F1D1D',
        marker_line_width=1.5
    )
    fig.update_layout(
        **THEME_DARK,
        coloraxis_showscale=False,
        margin=dict(l=40, r=20, t=50, b=40)
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    return fig

# 4. Gráfico circular: 10 ciudades con menor índice de mortalidad
def fig_menor_mortalidad(df: pd.DataFrame):
    conteo = df.groupby('MUNICIPIO').size().reset_index(name='NUM_MUERTES')
    conteo = conteo[conteo['MUNICIPIO'].notna() & (conteo['MUNICIPIO'].str.strip() != '')]
    bottom10 = conteo.nsmallest(10, 'NUM_MUERTES')
    
    fig = px.pie(
        bottom10,
        names='MUNICIPIO',
        values='NUM_MUERTES',
        title='<b>10 Municipios con Menor Número de Muertes Registradas</b>',
        hole=0.4,
        color_discrete_sequence=px.colors.diverging.Spectral
    )
    fig.update_traces(
        textinfo='label+value',
        textposition='inside',
        marker=dict(line=dict(color='#0F172A', width=2))
    )
    fig.update_layout(
        **{k: v for k, v in THEME_DARK.items() if k != 'plot_bgcolor'},
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

# 5. Tabla: 10 principales causas de muerte
def fig_tabla_causas(df: pd.DataFrame, df_causas: pd.DataFrame):
    conteo = df.groupby('COD_MUERTE').size().reset_index(name='TOTAL_CASOS')
    top10 = conteo.sort_values('TOTAL_CASOS', ascending=False).head(10)
    top10['COD_MUERTE'] = top10['COD_MUERTE'].astype(str).str.strip()
    
    # Obtener catálogo de causas con nombres normalizados
    catalogo = df_causas[['COD_MUERTE', 'DESCRIPCION']].drop_duplicates(subset=['COD_MUERTE'])
    catalogo['COD_MUERTE'] = catalogo['COD_MUERTE'].astype(str).str.strip()
    
    top10_merged = pd.merge(top10, catalogo, on='COD_MUERTE', how='left')
    top10_merged['DESCRIPCION'] = top10_merged['DESCRIPCION'].fillna("Descripción no clasificada")
    top10_merged['RANKING'] = range(1, len(top10_merged) + 1)
    
    top10_final = top10_merged[['RANKING', 'COD_MUERTE', 'DESCRIPCION', 'TOTAL_CASOS']]
    top10_final.columns = ['#', 'Código CIE-10', 'Nombre / Descripción de la Causa', 'Total Casos']
    
    fig = go.Figure(data=[go.Table(
        columnwidth=[40, 95, 480, 95],
        header=dict(
            values=list(top10_final.columns),
            fill_color='#1E293B',
            font=dict(color='#38BDF8', size=13, family='Segoe UI, Arial'),
            align=['center', 'center', 'left', 'center'],
            line=dict(color='#334155', width=1.5),
            height=35
        ),
        cells=dict(
            values=[
                top10_final['#'],
                top10_final['Código CIE-10'],
                top10_final['Nombre / Descripción de la Causa'],
                [f"{x:,d}" for x in top10_final['Total Casos']]
            ],
            fill_color='#0F172A',
            font=dict(color='#F8FAFC', size=12, family='Segoe UI, Arial'),
            align=['center', 'center', 'left', 'center'],
            line=dict(color='#334155', width=1),
            height=32
        )
    )])
    fig.update_layout(
        title='<b>Listado de las 10 Principales Causas de Muerte en Colombia</b>',
        paper_bgcolor='#0F172A',
        font=dict(color='#E2E8F0'),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

# 6. Gráfico de barras apiladas: Muertes por sexo en cada departamento
def fig_sexo_departamento(df: pd.DataFrame):
    df_dep = df.dropna(subset=['DEPARTAMENTO'])
    conteo = df_dep.groupby(['DEPARTAMENTO', 'SEXO_TXT']).size().reset_index(name='NUM_MUERTES')
    
    conteo['DEPARTAMENTO'] = conteo['DEPARTAMENTO'].replace({
        'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA': 'SAN ANDRÉS Y P.',
        'BOGOTÁ, D.C.': 'BOGOTÁ D.C.',
        'NORTE DE SANTANDER': 'N. DE SANTANDER'
    })
    
    dept_order = conteo.groupby('DEPARTAMENTO')['NUM_MUERTES'].sum().sort_values(ascending=False).index.tolist()
    
    fig = px.bar(
        conteo,
        x='DEPARTAMENTO',
        y='NUM_MUERTES',
        color='SEXO_TXT',
        title='<b>Comparación del Total de Muertes por Sexo en Cada Departamento</b>',
        labels={'NUM_MUERTES': 'Defunciones', 'DEPARTAMENTO': 'Departamento', 'SEXO_TXT': 'Sexo'},
        barmode='stack',
        category_orders={'DEPARTAMENTO': dept_order},
        color_discrete_map={
            'Masculino': '#0284C7',
            'Femenino': '#EC4899',
            'Indeterminado': '#94A3B8'
        }
    )
    layout_args = {k: v for k, v in THEME_DARK.items() if k != 'legend'}
    fig.update_layout(
        **layout_args,
        xaxis_tickangle=-45,
        margin=dict(l=40, r=20, t=50, b=80),
        legend=dict(title=dict(text='Sexo', font=dict(color='#CBD5E1')), orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#CBD5E1'))
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155', tickformat=":,d")
    return fig

# 7. Histograma: Distribución de muertes por Ciclo de Vida
def fig_ciclo_vida(df: pd.DataFrame, choices: list):
    conteo = df.groupby('categoría_mortalidad').size().reindex(choices, fill_value=0).reset_index(name='NUM_MUERTES')
    conteo.columns = ['CATEGORIA', 'NUM_MUERTES']
    
    fig = px.bar(
        conteo,
        x='CATEGORIA',
        y='NUM_MUERTES',
        text='NUM_MUERTES',
        color='NUM_MUERTES',
        color_continuous_scale='Tealgrn',
        title='<b>Distribución de Muertes por Ciclo de Vida (GRUPO_EDAD1)</b>',
        labels={'CATEGORIA': 'Etapa del ciclo de vida', 'NUM_MUERTES': 'Total de defunciones'},
        category_orders={'CATEGORIA': choices}
    )
    fig.update_traces(
        texttemplate='%{text:,d}',
        textposition='outside',
        marker_line_color='#065F46',
        marker_line_width=1.2
    )
    fig.update_layout(
        **THEME_DARK,
        xaxis_tickangle=-35,
        coloraxis_showscale=False,
        margin=dict(l=40, r=20, t=50, b=70)
    )
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155', tickformat=":,d")
    return fig
