import os
import pandas as pd
from src.classification_models import treinar_random_forest
from src.config import REPORTS_DIR

def executar_estudo_robustez(df_modelo):
    testes = {
        "Baseline (Todas as Features)": ['receita_total', 'qtde_pedidos', 'pct_receita_servicos', 'foco_em_servicos'],
        "Sem 'receita_total'": ['qtde_pedidos', 'pct_receita_servicos', 'foco_em_servicos'],
        "Sem 'pct_receita_servicos'": ['receita_total', 'qtde_pedidos', 'foco_em_servicos'],
        "Sem 'qtde_pedidos'": ['receita_total', 'pct_receita_servicos', 'foco_em_servicos'],
        "Sem 'foco_em_servicos'": ['receita_total', 'qtde_pedidos', 'pct_receita_servicos'],
        "Apenas Features de Receita": ['receita_total', 'pct_receita_servicos'],
        "Apenas Frequência e Mix": ['qtde_pedidos', 'foco_em_servicos']
    }

    tabela = []
    for nome, feats in testes.items():
        _, acc, rep = treinar_random_forest(df_modelo, feats)
        tabela.append({
            "Teste de Robustez": nome,
            "Acurácia": f"{acc:.2%}",
            "Precisão (Churn)": f"{rep['1']['precision']:.2%}",
            "Recall (Churn)": f"{rep['1']['recall']:.2%}",
            "F1-Score (Churn)": f"{rep['1']['f1-score']:.2%}"
        })

    df_res = pd.DataFrame(tabela)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df_res.to_csv(os.path.join(REPORTS_DIR, "metricas_robustez.csv"), index=False)
    return df_res
