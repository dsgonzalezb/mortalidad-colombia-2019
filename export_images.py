import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from load_data import load_data
from figures import (
    fig_mapa, fig_lineas_mes, fig_ciudades_violentas,
    fig_menor_mortalidad, fig_tabla_causas, fig_sexo_departamento,
    fig_ciclo_vida
)

os.makedirs("images", exist_ok=True)
df_total, df_causas, choices = load_data()

figures = {
    "1_mapa_mortalidad.png": fig_mapa(df_total),
    "2_lineas_mes.png": fig_lineas_mes(df_total),
    "3_ciudades_violentas.png": fig_ciudades_violentas(df_total),
    "4_menor_mortalidad.png": fig_menor_mortalidad(df_total),
    "5_tabla_causas.png": fig_tabla_causas(df_total, df_causas),
    "6_sexo_departamento.png": fig_sexo_departamento(df_total),
    "7_ciclo_vida.png": fig_ciclo_vida(df_total, choices)
}

print("Iniciando exportación de imágenes...")
for name, fig in figures.items():
    path = os.path.join("images", name)
    try:
        fig.write_image(path, width=1100, height=600, scale=2)
        print(f"Exportado: {name} ({os.path.getsize(path)} bytes)")
    except Exception as e:
        print(f"Error al exportar {name}: {e}")

print("Exportación completa.")

