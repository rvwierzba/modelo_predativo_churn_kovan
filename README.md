# Modelo Preditivo de Churn B2B — Kovan Technologies

## Objetivo de Negócio
Prever a erosão silenciosa de receita no segmento Mid-Market da Kovan Technologies (Caminho B), validando o impacto do mix de serviços vs. hardware.

## Tabela Comparativa do Estudo de Robustez

| Teste de Robustez | Acurácia | Precisão (Churn) | Recall (Churn) | F1-Score (Churn) |
|---|---|---|---|---|
| Baseline (Todas as Features) | 72.94% | 35.45% | 40.10% | 37.63% |
| Sem receita_total | 71.85% | 33.91% | 39.59% | 36.53% |
| Sem pct_receita_servicos | 72.55% | 34.78% | 38.55% | 36.56% |
| Sem qtde_pedidos | 72.80% | 35.12% | 39.76% | 37.28% |
| Sem foco_em_servicos | 72.90% | 35.40% | 40.10% | 37.59% |
| Apenas Features de Receita | 72.76% | 35.15% | 39.93% | 37.38% |
| Apenas Frequência e Mix | 67.97% | 27.61% | 34.08% | 30.50% |

## Conclusões Principais
1. Importância Financeira: Retirar receita_total causa a maior queda de F1-Score e precisão do modelo.
2. Impacto do Portfólio: O mix de serviços (pct_receita_servicos) é a segunda feature mais crítica, confirmando que a ausência de hardware eleva o churn para 61,4%.

## Como Executar
pip install -r requirements.txt
python main.py
