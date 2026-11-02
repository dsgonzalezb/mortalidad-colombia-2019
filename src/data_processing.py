import os
import numpy as np
import pandas as pd

CICLO_VIDA_CHOICES = [
    "Mortalidad neonatal",
    "Mortalidad infantil",
    "Primera infancia",
    "Niñez",
    "Adolescencia",
    "Juventud",
    "Adultez temprana",
    "Adultez intermedia",
    "Vejez",
    "Longevidad / Centenarios",
    "Edad desconocida"
]

MESES_MAP = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

SEXO_MAP = {
    1: "Masculino",
    2: "Femenino",
    3: "Indeterminado"
}

# Coordenadas geográficas oficiales de los 33 departamentos de Colombia (DANE / DIVIPOLA)
COORDENADAS_DEPARTAMENTOS = {
    5:  {"LATITUD": 6.702032, "LONGITUD": -75.504557},  # ANTIOQUIA
    8:  {"LATITUD": 10.677010, "LONGITUD": -74.965219}, # ATLÁNTICO
    11: {"LATITUD": 4.316108, "LONGITUD": -74.181073},  # BOGOTÁ, D.C.
    13: {"LATITUD": 8.079797, "LONGITUD": -74.235148},  # BOLÍVAR
    15: {"LATITUD": 5.891673, "LONGITUD": -72.627881},  # BOYACÁ
    17: {"LATITUD": 5.280140, "LONGITUD": -75.274983},  # CALDAS
    18: {"LATITUD": 0.798556, "LONGITUD": -73.959468},  # CAQUETÁ
    19: {"LATITUD": 2.396834, "LONGITUD": -76.824233},  # CAUCA
    20: {"LATITUD": 9.536660, "LONGITUD": -73.517832},  # CESAR
    23: {"LATITUD": 8.358550, "LONGITUD": -75.792009},  # CÓRDOBA
    25: {"LATITUD": 4.771121, "LONGITUD": -74.431111},  # CUNDINAMARCA
    27: {"LATITUD": 5.397582, "LONGITUD": -76.942811},  # CHOCÓ
    41: {"LATITUD": 2.570143, "LONGITUD": -75.584348},  # HUILA
    44: {"LATITUD": 11.476870, "LONGITUD": -72.429511}, # LA GUAJIRA
    47: {"LATITUD": 10.247384, "LONGITUD": -74.261757}, # MAGDALENA
    50: {"LATITUD": 3.345563, "LONGITUD": -72.956460},  # META
    52: {"LATITUD": 1.571095, "LONGITUD": -77.870205},  # NARIÑO
    54: {"LATITUD": 8.095138, "LONGITUD": -72.881883},  # NORTE DE SANTANDER
    63: {"LATITUD": 4.455242, "LONGITUD": -75.689629},  # QUINDÍO
    66: {"LATITUD": 5.240757, "LONGITUD": -76.002445},  # RISARALDA
    68: {"LATITUD": 6.693633, "LONGITUD": -73.486009},  # SANTANDER
    70: {"LATITUD": 9.064941, "LONGITUD": -75.109818},  # SUCRE
    73: {"LATITUD": 4.034773, "LONGITUD": -75.255827},  # TOLIMA
    76: {"LATITUD": 3.569859, "LONGITUD": -76.628504},  # VALLE DEL CAUCA
    81: {"LATITUD": 6.569577, "LONGITUD": -70.967324},  # ARAUCA
    85: {"LATITUD": 5.404064, "LONGITUD": -71.601881},  # CASANARE
    86: {"LATITUD": 0.367303, "LONGITUD": -75.514062},  # PUTUMAYO
    88: {"LATITUD": 12.543115, "LONGITUD": -81.717624}, # SAN ANDRÉS Y PROVIDENCIA
    91: {"LATITUD": -1.546228, "LONGITUD": -71.502129}, # AMAZONAS
    94: {"LATITUD": 2.727843, "LONGITUD": -68.816613},  # GUAINÍA
    95: {"LATITUD": 1.924532, "LONGITUD": -72.128596},  # GUAVIARE
    97: {"LATITUD": 0.646246, "LONGITUD": -70.561406},  # VAUPÉS
    99: {"LATITUD": 4.713557, "LONGITUD": -69.414000},  # VICHADA
}

def process_raw_data(data_dir: str):
    """
    Carga y procesa exclusivamente los 3 archivos solicitados en las indicaciones:
    1. Datos de mortalidad: Anexo1.NoFetal2019_CE_15-03-23.xlsx
    2. Nombres de causas de muerte: Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx
    3. División Político-Administrativa: Divipola_CE_.xlsx
    """
    path_mortalidad = os.path.join(data_dir, "Anexo1.NoFetal2019_CE_15-03-23.xlsx")
    path_causas = os.path.join(data_dir, "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx")
    path_divipola = os.path.join(data_dir, "Divipola_CE_.xlsx")

    # Lectura de los 3 archivos oficiales
    df_mortalidad = pd.read_excel(path_mortalidad)
    df_anexo2 = pd.read_excel(path_causas, skiprows=8)
    df_divipola = pd.read_excel(path_divipola).dropna(how="all")

    # Construcción de catálogo robusto (códigos de 4 y 3 caracteres)
    c4 = df_anexo2.iloc[:, [4, 5]].dropna().drop_duplicates()
    c4.columns = ["COD_MUERTE", "DESCRIPCION"]
    c4["COD_MUERTE"] = c4["COD_MUERTE"].astype(str).str.strip()
    c4["DESCRIPCION"] = c4["DESCRIPCION"].astype(str).str.strip()

    c3 = df_anexo2.iloc[:, [2, 3]].dropna().drop_duplicates()
    c3.columns = ["COD_MUERTE", "DESCRIPCION"]
    c3["COD_MUERTE"] = c3["COD_MUERTE"].astype(str).str.strip()
    c3["DESCRIPCION"] = c3["DESCRIPCION"].astype(str).str.strip()

    df_causas_clean = pd.concat([c4, c3]).drop_duplicates(subset=["COD_MUERTE"])

    # Homologación de códigos
    df_divipola["COD_DEPARTAMENTO"] = pd.to_numeric(df_divipola["COD_DEPARTAMENTO"], errors="coerce")
    df_mortalidad["COD_MUERTE"] = df_mortalidad["COD_MUERTE"].astype(str).str.strip()

    # Merge mortalidad con catálogo CIE-10
    df_mortalidad_causa = pd.merge(
        df_mortalidad,
        df_causas_clean,
        on="COD_MUERTE",
        how="left"
    )

    # Coordenadas geográficas por departamento a partir del diccionario oficial
    df_coords = pd.DataFrame.from_dict(COORDENADAS_DEPARTAMENTOS, orient="index").reset_index()
    df_coords.columns = ["COD_DEPARTAMENTO", "LATITUD", "LONGITUD"]

    # Integración con DIVIPOLA
    df_geo = pd.merge(df_divipola, df_coords, on="COD_DEPARTAMENTO", how="left")
    df_geo = df_geo[["COD_DANE", "LATITUD", "LONGITUD", "DEPARTAMENTO", "MUNICIPIO"]].drop_duplicates(subset=["COD_DANE"])

    # Integración final
    df_mortalidad_total = pd.merge(df_mortalidad_causa, df_geo, on="COD_DANE", how="left")

    # Clasificación por Ciclo de Vida (según la tabla de referencia del enunciado)
    conditions = [
        (df_mortalidad_total["GRUPO_EDAD1"] <= 4),
        (df_mortalidad_total["GRUPO_EDAD1"].between(5, 6)),
        (df_mortalidad_total["GRUPO_EDAD1"].between(7, 8)),
        (df_mortalidad_total["GRUPO_EDAD1"].between(9, 10)),
        (df_mortalidad_total["GRUPO_EDAD1"] == 11),
        (df_mortalidad_total["GRUPO_EDAD1"].between(12, 13)),
        (df_mortalidad_total["GRUPO_EDAD1"].between(14, 16)),
        (df_mortalidad_total["GRUPO_EDAD1"].between(17, 19)),
        (df_mortalidad_total["GRUPO_EDAD1"].between(20, 24)),
        (df_mortalidad_total["GRUPO_EDAD1"].between(25, 28)),
        (df_mortalidad_total["GRUPO_EDAD1"] == 29),
    ]

    df_mortalidad_total["categoría_mortalidad"] = np.select(
        conditions,
        CICLO_VIDA_CHOICES,
        default="Edad desconocida"
    )

    df_mortalidad_total["SEXO_TXT"] = df_mortalidad_total["SEXO"].map(SEXO_MAP).fillna("Indeterminado")
    df_mortalidad_total["MES_NOMBRE"] = df_mortalidad_total["MES"].map(MESES_MAP)

    return df_mortalidad_total, df_causas_clean, CICLO_VIDA_CHOICES
