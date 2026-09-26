import re
import pandas as pd
import numpy as np
from src.data_loader import carregar_dados

def construir_dataset_temporal(
    data_dict=None,
    train_years=[2021, 2022, 2023],
    target_years=[2024, 2025, 2026],
    target_mode="solucao_b",
    erosion_threshold=0.15,
    segment_filter="MID MARKET"
):
    """
    Constrói base analítica temporal completa unificando as 5 fontes de dados da Kovan.
    
    Parâmetros:
    - train_years: Anos utilizados para a janela de observação (ex: 2021, 2022, 2023 -> 3 anos)
    - target_years: Anos previstos para validação/teste (ex: 2024, 2025, 2026 -> Anos 4 e 5)
    - target_mode: 'solucao_b' (Erosão Silenciosa de Receita/Mix) ou 'solucao_a' (Ruptura Total de Contrato)
    - erosion_threshold: Limiar percentual para queda de receita (ex: 0.15 = 15%)
    - segment_filter: Filtro de segmento ('MID MARKET', 'STRATEGIC ACCOUNT', 'ALL', etc.)
    """
    if data_dict is None:
        data_dict = carregar_dados()

    df1 = data_dict["df1"].copy()
    df2 = data_dict["df2"].copy()
    df3 = data_dict["df3"].copy()
    df4 = data_dict["df4"].copy()

    # Processamento de datas e anos no Dataset 1 (Transacional mensal)
    df1['periodo_dt'] = pd.to_datetime(df1['periodo'] + '-01')
    df1['year'] = df1['periodo_dt'].dt.year

    # Filtrar segmento se solicitado
    if segment_filter and segment_filter.upper() != "ALL":
        df1 = df1[df1['segment'] == segment_filter.upper()].copy()
        df4 = df4[df4['segment'] == segment_filter.upper()].copy()

    # Separar janela de treino (observação) e janela de teste (target)
    train_mask = df1['year'].isin(train_years)
    target_mask = df1['year'].isin(target_years)

    df1_train = df1[train_mask]
    df1_target = df1[target_mask]

    # Agregação por Conta no Período de Observação (Train Window)
    train_acc = df1_train.groupby(['account_id', 'segment', 'country']).agg(
        receita_media_obs=('receita_usd', 'mean'),
        receita_total_obs=('receita_usd', 'sum'),
        receita_std_obs=('receita_usd', 'std'),
        pedidos_total_obs=('qtd_pedidos', 'sum'),
        pedidos_medio_obs=('qtd_pedidos', 'mean'),
        meses_ativos_obs=('periodo', 'nunique'),
        eventos_churn_obs=('churn_label', 'sum')
    ).reset_index()

    # Calcular tendência temporal no período de treino (Último ano de treino vs Primeiro ano)
    primeiro_ano_train = min(train_years)
    ultimo_ano_train = max(train_years)

    rec_inicio = df1_train[df1_train['year'] == primeiro_ano_train].groupby('account_id')['receita_usd'].sum().reset_index().rename(columns={'receita_usd': 'rec_inicio_train'})
    rec_fim = df1_train[df1_train['year'] == ultimo_ano_train].groupby('account_id')['receita_usd'].sum().reset_index().rename(columns={'receita_usd': 'rec_fim_train'})

    train_acc = train_acc.merge(rec_inicio, on='account_id', how='left').merge(rec_fim, on='account_id', how='left')
    train_acc['rec_inicio_train'] = train_acc['rec_inicio_train'].fillna(0)
    train_acc['rec_fim_train'] = train_acc['rec_fim_train'].fillna(0)
    train_acc['variacao_receita_obs'] = (train_acc['rec_fim_train'] - train_acc['rec_inicio_train']) / (train_acc['rec_inicio_train'] + 1000.0)

    # 1. Unir Dataset 4 (Firmografia e Relacionamento)
    train_acc = train_acc.merge(df4[['account_id', 'industry', 'tempo_como_cliente', 'canal_aquisicao']], on='account_id', how='left')

    # 2. Unir Dataset 2 (Mix de Portfólio: Serviços vs Hardware)
    d2_serv = df2[df2['Brand'] == 'SERVICES'].groupby('account_id')['pct_receita'].mean().reset_index().rename(columns={'pct_receita': 'pct_servicos'})
    d2_hw = df2[df2['Brand'].isin(['NOTEBOOK', 'DESKTOP', 'WORKSTATION'])].groupby('account_id')['pct_receita'].sum().reset_index().rename(columns={'pct_receita': 'pct_hardware'})
    d2_mix = df2.groupby('account_id').agg(total_skus=('qtd_skus_distintos', 'sum'), num_marcas=('Brand', 'nunique')).reset_index()

    train_acc = train_acc.merge(d2_serv, on='account_id', how='left').merge(d2_hw, on='account_id', how='left').merge(d2_mix, on='account_id', how='left')
    train_acc['pct_servicos'] = train_acc['pct_servicos'].fillna(0.0)
    train_acc['pct_hardware'] = train_acc['pct_hardware'].fillna(0.0)
    train_acc['total_skus'] = train_acc['total_skus'].fillna(0)
    train_acc['num_marcas'] = train_acc['num_marcas'].fillna(0)
    train_acc['foco_em_servicos'] = (train_acc['pct_servicos'] > 0.8).astype(int)

    # 3. Unir Dataset 3 (Engajamento Comercial / CRM / Contatos do Account Manager)
    df3['year'] = df3['periodo'].apply(lambda x: int(str(x).split('-')[0]))
    df3_train = df3[df3['year'].isin(train_years)]

    d3_agg = df3_train.groupby('account_id').agg(
        contatos_realizados_obs=('contatos_realizados', 'sum'),
        dias_sem_contato_medio_obs=('dias_sem_contato', 'mean'),
        opps_abertas_obs=('oportunidades_abertas', 'sum'),
        opps_ganhas_obs=('oportunidades_ganhas', 'sum')
    ).reset_index()
    d3_agg['taxa_conversao_pipeline'] = d3_agg['opps_ganhas_obs'] / (d3_agg['opps_abertas_obs'] + 1.0)

    train_acc = train_acc.merge(d3_agg, on='account_id', how='left')
    train_acc['contatos_realizados_obs'] = train_acc['contatos_realizados_obs'].fillna(0)
    train_acc['dias_sem_contato_medio_obs'] = train_acc['dias_sem_contato_medio_obs'].fillna(90)
    train_acc['opps_abertas_obs'] = train_acc['opps_abertas_obs'].fillna(0)
    train_acc['opps_ganhas_obs'] = train_acc['opps_ganhas_obs'].fillna(0)
    train_acc['taxa_conversao_pipeline'] = train_acc['taxa_conversao_pipeline'].fillna(0)

    # Agregação da Janela Target (Anos 4 e 5)
    target_acc = df1_target.groupby('account_id').agg(
        receita_total_target=('receita_usd', 'sum'),
        churn_max_target=('churn_label', 'max'),
        meses_ativos_target=('periodo', 'nunique')
    ).reset_index()

    # Unir observações de treino com o resultado real nos Anos 4 e 5
    dataset = train_acc.merge(target_acc, on='account_id', how='left')
    dataset['receita_total_target'] = dataset['receita_total_target'].fillna(0)
    dataset['churn_max_target'] = dataset['churn_max_target'].fillna(1) # Conta sem pedidos no período
    dataset['meses_ativos_target'] = dataset['meses_ativos_target'].fillna(0)

    # Definição dos Alvos (Targets) conforme o Case:
    # Solução B (Erosão Silenciosa): Queda de receita >= erosion_threshold em relação ao nível de encerramento do treino OU churn
    num_anos_target = len(target_years)
    num_anos_train = len(train_years)
    fator_escala = num_anos_target / num_anos_train

    dataset['target_solucao_b'] = (
        (dataset['churn_max_target'] == 1) |
        (dataset['receita_total_target'] < dataset['rec_fim_train'] * (1.0 - erosion_threshold) * num_anos_target)
    ).astype(int)

    # Solução A (Ruptura Total): Churn binário formal no sistema
    dataset['target_solucao_a'] = dataset['churn_max_target'].astype(int)

    # Escolha do target ativo para a modelagem
    if target_mode == "solucao_a":
        dataset['target'] = dataset['target_solucao_a']
    else:
        dataset['target'] = dataset['target_solucao_b']

    # Codificação de variáveis categóricas
    dataset_encoded = pd.get_dummies(dataset, columns=['segment', 'country', 'industry', 'canal_aquisicao'], drop_first=True)
    dataset_encoded.columns = [re.sub(r'[^\w]', '_', c) for c in dataset_encoded.columns]

    # Separar colunas de metadados das colunas de atributo preditivo (X)
    ignore_cols = [
        'account_id', 'receita_total_target', 'churn_max_target',
        'meses_ativos_target', 'target_solucao_b', 'target_solucao_a', 'target'
    ]
    feature_cols = [c for c in dataset_encoded.columns if c not in ignore_cols]

    return dataset_encoded, feature_cols, dataset
