import pandas as pd
from src.config import TARGET_SEGMENT

def construir_features(df_raw, df_portfolio):
    df_agg = df_raw.groupby(['account_id', 'quarter', 'segment']).agg(
        receita_total=('total_value_usd', 'sum'),
        qtde_pedidos=('invoice_no', 'nunique'),
        churn_label=('churn_label', 'first')
    ).reset_index()

    df_servicos = df_portfolio[df_portfolio['Brand'] == 'SERVICES'][['account_id', 'pct_receita']].copy()
    df_servicos.rename(columns={'pct_receita': 'pct_receita_servicos'}, inplace=True)

    df_merged = pd.merge(df_agg, df_servicos, on='account_id', how='left')
    df_merged['pct_receita_servicos'] = df_merged['pct_receita_servicos'].fillna(0.0)
    df_merged['foco_em_servicos'] = (df_merged['pct_receita_servicos'] > 0.9).astype(int)

    df_mid = df_merged[df_merged['segment'] == TARGET_SEGMENT].copy()
    return df_mid
