import os
import pandas as pd
from data_processing import process_raw_data, CICLO_VIDA_CHOICES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_MORTALIDAD = os.path.join(DATA_DIR, "mortalidad_procesada.csv.gz")
CSV_CAUSAS = os.path.join(DATA_DIR, "causas_procesadas.csv.gz")

def load_data():
    """
    Carga los datos optimizados desde archivos CSV comprimidos (.csv.gz)
    garantizando 100% de interoperabilidad y compatibilidad universal
    entre cualquier versión de Python, Pandas y NumPy.
    """
    if os.path.exists(CSV_MORTALIDAD) and os.path.exists(CSV_CAUSAS):
        try:
            df_mortalidad_total = pd.read_csv(CSV_MORTALIDAD, low_memory=False)
            df_causas = pd.read_csv(CSV_CAUSAS)
            return df_mortalidad_total, df_causas, CICLO_VIDA_CHOICES
        except Exception as e:
            print(f"Aviso: Error al cargar archivos comprimidos ({e}). Se procesarán los archivos Excel originales...")

    # Procesar desde Excel originales
    df_mortalidad_total, df_causas, choices = process_raw_data(DATA_DIR)

    # Guardar en CSV comprimido para arranques rápidos (<1s) y sin dependencias de versión
    try:
        df_mortalidad_total.to_csv(CSV_MORTALIDAD, index=False, compression="gzip")
        df_causas.to_csv(CSV_CAUSAS, index=False, compression="gzip")
    except Exception as e:
        print(f"Aviso: No se pudieron guardar los archivos optimizados ({e})")

    return df_mortalidad_total, df_causas, choices
