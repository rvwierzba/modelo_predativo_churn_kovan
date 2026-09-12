import os
import pandas as pd
from src.config import EXCEL_PATH, SHEET_RAW, SHEET_PORTFOLIO

def carregar_dados():
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {EXCEL_PATH}")
    xls = pd.ExcelFile(EXCEL_PATH)
    df_raw = pd.read_excel(xls, sheet_name=SHEET_RAW)
    df_portfolio = pd.read_excel(xls, sheet_name=SHEET_PORTFOLIO)
    df_raw.columns = df_raw.columns.str.strip()
    df_portfolio.columns = df_portfolio.columns.str.strip()
    return df_raw, df_portfolio
