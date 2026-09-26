import pandas as pd
import numpy as np

def simular_impacto_financeiro(raw_dataset_test, y_probs, threshold=0.50, max_am_capacity=138):
    """
    Calcula a preservação de NRR e valor financeiro protegido (R$) com base na priorização
    das contas com maior score de risco no conjunto de teste, respeitando a capacidade comercial de Account Managers (138 planos/trimestre).
    """
    df = raw_dataset_test.copy().reset_index(drop=True)
    df['risk_score'] = y_probs
    df['predicted_risk'] = (df['risk_score'] >= threshold).astype(int)

    # Receita em risco por ano é a receita do ano base de encerramento do treino
    df['receita_anual_em_risco'] = df['rec_fim_train']

    # Ordenar por maior risco e maior valor em risco
    df_sorted = df.sort_values(by=['predicted_risk', 'risk_score', 'receita_anual_em_risco'], ascending=[False, False, False])

    # Contas priorizadas pela capacidade comercial dos Account Managers
    contas_sinalizadas = df_sorted[df_sorted['predicted_risk'] == 1]
    contas_priorizadas_am = contas_sinalizadas.head(max_am_capacity)

    receita_total_identificada = contas_sinalizadas['receita_anual_em_risco'].sum()
    receita_protegida_capacidade = contas_priorizadas_am['receita_anual_em_risco'].sum()
    total_contas_sinalizadas = len(contas_sinalizadas)

    # Estimativa de recuperação de NRR (assumindo 60% de eficácia dos planos de intervenção)
    receita_preservada_nrr = receita_protegida_capacidade * 0.60

    return {
        "total_contas_analisadas": len(df),
        "total_contas_sinalizadas": int(total_contas_sinalizadas),
        "contas_atendidas_am": len(contas_priorizadas_am),
        "teto_capacidade_am": max_am_capacity,
        "receita_total_identificada_usd": float(receita_total_identificada),
        "receita_protegida_capacidade_usd": float(receita_protegida_capacidade),
        "receita_preservada_nrr_usd": float(receita_preservada_nrr)
    }

def gerar_tabela_comparativa_robustez(model_results_dict):
    """
    Gera tabela de comparação para o README entre a abordagem Baseline e a Nova Arquitetura Preditiva.
    """
    rows = []
    for test_name, res in model_results_dict.items():
        m = res["metrics"]
        rows.append({
            "Abordagem / Teste": test_name,
            "Acurácia": f"{m['accuracy']:.2%}",
            "Precisão": f"{m['precision']:.2%}",
            "Recall": f"{m['recall']:.2%}",
            "F1-Score": f"{m['f1_score']:.2%}",
            "ROC-AUC": f"{m['roc_auc']:.4f}"
        })
    return pd.DataFrame(rows)
