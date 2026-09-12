import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

def executar_sarima_receita(df_raw):
    df_mid = df_raw[df_raw['segment'] == 'MID MARKET'].copy()
    serie = df_mid.groupby('periodo')['total_value_usd'].sum().sort_index()
    modelo = SARIMAX(serie, order=(1, 1, 1), seasonal_order=(1, 1, 0, 4))
    res = modelo.fit(disp=False)
    forecast = res.forecast(steps=4)
    return res, serie, forecast
