import os
import pandas as pd
from src.config import EXCEL_PATH, SHEETS

_cached_data = None

def carregar_dados(force_reload=False):
    """
    Carrega e armazena em cache os 5 datasets do estudo de caso Kovan LATAM:
    - Dataset 1: Transações mensais agregadas por conta
    - Dataset 2: Mix de produtos e participação de marcas (Services vs Hardware)
    - Dataset 3: Atividade comercial de CRM e contatos de Account Managers
    - Dataset 4: Atributos da conta (Firmografia, Tempo de Relacionamento, Canal)
    - raw data: Transações brutas por item de linha
    """
    global _cached_data
    if _cached_data is not None and not force_reload:
        return _cached_data

    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Arquivo oficial não encontrado em: {EXCEL_PATH}")

    print(f"[DataLoader] Lendo pastas de trabalho de '{EXCEL_PATH}'...")
    xls = pd.ExcelFile(EXCEL_PATH)

    df1 = pd.read_excel(xls, sheet_name=SHEETS["D1"])
    df2 = pd.read_excel(xls, sheet_name=SHEETS["D2"])
    df3 = pd.read_excel(xls, sheet_name=SHEETS["D3"])
    df4 = pd.read_excel(xls, sheet_name=SHEETS["D4"])
    df_raw = pd.read_excel(xls, sheet_name=SHEETS["RAW"])

    # Normalizar nomes de colunas (remover espaços extras)
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()
    df3.columns = df3.columns.str.strip()
    df4.columns = df4.columns.str.strip()
    df_raw.columns = df_raw.columns.str.strip()

    _cached_data = {
        "df1": df1,
        "df2": df2,
        "df3": df3,
        "df4": df4,
        "df_raw": df_raw
    }

    print(f"[DataLoader] Sucesso: {len(df1)} registros mensais, {len(df4)} contas únicas.")
    return _cached_data
