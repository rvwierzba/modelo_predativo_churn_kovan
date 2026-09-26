# Modelo Preditivo de Churn & Erosão Silenciosa B2B — Kovan Technologies LATAM

> **Solução B (Erosão Silenciosa de Receita e Mix)** — Sistema preditivo para prevenção contínua de contração de contas corporativas B2B e proteção de NRR.

---

## 🚀 Resumo Executivo & Resultados Obtidos

Diante da queda do **Net Revenue Retention (NRR)** do segmento estratégico de 109% para 93% (custando **R$ 248.000.000** em contração de receita anualizada), a **Nova Arquitetura Preditiva de IA** superou de forma expressiva os benchmarks anteriores.

Ao implementar uma validação temporal rigorosa (treinamento sobre **3 Anos de histórico [2021–2023]** para prever o risco de churn/erosão nos **Anos 4 e 5 [2024–2026]**), o modelo alcançou um **F1-Score de 95,81%** e um **ROC-AUC de 0.9717**, eliminando os altos índices de falsos positivos e a baixa precisão do script legado.

### 📊 Tabela Comparativa de Desempenho e Robustez

| Abordagem / Modelo | Acurácia | Precisão | Recall | F1-Score | ROC-AUC | Ganho vs. Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nova Arquitetura (XGBoost — Solução B)** | **93,09%** | **92,70%** | **99,13%** | **95,81%** | **0.9717** | **+58,18% em F1** |
| **Nova Arquitetura (LightGBM — Solução B)** | **92,57%** | **92,83%** | **98,26%** | **95,47%** | **0.9716** | **+57,84% em F1** |
| **Random Forest Otimizado (Solução B)** | **91,36%** | **94,19%** | **95,01%** | **94,60%** | **0.9627** | **+56,97% em F1** |
| **Modelo de Ruptura Binária (Solução A)** | **100,00%** | **100,00%** | **100,00%** | **100,00%** | **1.0000** | **Alvo Binário** |
| *Baseline Legado (Script Anterior)* | *72,94%* | *35,45%* | *40,10%* | *37,63%* | *0.6120* | *Referência* |

---

## 💡 Contexto do Negócio & Caso Kovan LATAM (PDF)

- **Desafio do Comitê de Receita**: Substituir a avaliação manual por um score preditivo transacional publicado diretamente no CRM corporativo.
- **Dilema de Negócio**:
  - **Caminho A (Sinal de Ruptura)**: Binário e preciso, porém muito tardio (prevalece em apenas 2,1% dos casos; quando dispara, o contrato substituto já foi assinado pelo concorrente).
  - **Caminho B (Erosão Silenciosa / Solução B — Adotado)**: Preditivo e contínuo. Ataca a causa-raiz da perda de 18,1 pontos percentuais de NRR em contas que continuam comprando, porém com menor volume ou mix estreitado (ex: Grupo Talvera).
- **Capacidade Operacional de AMs**: A força de vendas de 46 Account Managers possui capacidade praticável de até **138 planos de intervenção estruturados por trimestre** (3 por AM). O modelo prioriza automaticamente as contas de maior valor em risco até o teto de 138 planos.

---

## 🛠️ Estrutura do Repositório

```
modelo_predativo_churn_kovan/
├── main.py                     # Pipeline principal: treinamento, joblib e exportação de dados
├── requirements.txt            # Dependências Python
├── README.md                   # Documentação executiva completa
├── data/                       # Base de dados oficial (Excel 5 Anos)
│   └── datasets_case_modulo2_5yrs.xlsx
├── models_saved/               # Modelo treinado salvo em formato .joblib
│   └── kovan_churn_model.joblib
├── reports/                    # Relatórios exportados em CSV
│   ├── metricas_robustez.csv
│   └── benchmark_comparativo.csv
├── src/                        # Código-fonte modular do modelo
│   ├── __init__.py
│   ├── config.py               # Configurações globais e constantes de negócio
│   ├── data_loader.py          # Carregamento e caching dos 5 datasets
│   ├── feature_engineering.py  # Extração temporal de atributos, lags e alvos
│   ├── models.py               # Treinamento ML, XGBoost/LightGBM e joblib persistence
│   └── evaluator.py            # Simulação de NRR e impacto financeiro
├── static/                     # Dashboard Executivo Front-End (Standalone HTML/CSS/JS)
│   ├── index.html              # Interface estática executiva (English / Dark Glassmorphism)
│   ├── style.css               # Design system responsivo
│   ├── app.js                  # Lógica de upload do .joblib, filtros e gráficos
│   └── model_data.json         # Payload de dados estático
└── agents/ e .agents/          # Documentação dos Agentes Especialistas
    ├── data_analyst_agent.md
    ├── feature_engineer_agent.md
    ├── business_evaluator_agent.md
    ├── executive_presenter_agent.md
    └── system_architect_agent.md
```

---

## ⚡ Como Executar a Aplicação

> **⚠️ ATENÇÃO**: Colocar o arquivo `datasets_case_modulo2_5yrs.xlsx` dentro da pasta `data/` (tamanho > 50MB, não versionado diretamente no Git).

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o Pipeline de Treinamento e Gerar o Modelo `.joblib`
```bash
python main.py
```

### 3. Visualizar o Painel Executivo Front-End
Abra o arquivo `static/index.html` diretamente no navegador (duplo clique) e faça o upload do modelo `models_saved/kovan_churn_model.joblib` para explorar os dados, gráficos e a fila de priorização comercial.
