# 📑 Contratos de Dados e Schemas de Comunicação

> **Especificação dos Protocolos de Integração (Frontend ↔ n8n ↔ Agentes)**  
> **Sistema Multi-Agente Kovan LATAM**

---

## 1. Payload de Requisição HTTP POST (Frontend → Webhook n8n)

Enviado pelo cliente `index.html` ao endpoint configurado no Bloco 03.

### Schema JSON:
```json
{
  "sessionId": "kovan-sessao-1718000000000",
  "pergunta": "Qual é o diagnóstico das 5 contas com maior risco e quais planos devem ser priorizados para a equipe de KAMs?",
  "modelo_llm": "google/gemini-2.5-flash",
  "modelo": {
    "auc": 0.842,
    "acuracia": 0.815,
    "f1": 0.768,
    "sensibilidade": 0.792,
    "especificidade": 0.831,
    "coeficientes": {
      "intercept": 0.412,
      "qtd_pedidos": -0.684,
      "receita_usd": -0.521,
      "tempo_como_cliente": -0.315
    }
  },
  "contas": [
    {
      "account_id": "ACC-10492",
      "segment": "Enterprise",
      "country": "Brazil",
      "receita_usd": 1250000,
      "qtd_pedidos": 14,
      "probabilidade": 0.742,
      "risco": "alto"
    },
    {
      "account_id": "ACC-83921",
      "segment": "Mid-Market",
      "country": "Mexico",
      "receita_usd": 480000,
      "qtd_pedidos": 6,
      "probabilidade": 0.615,
      "risco": "alto"
    }
  ],
  "planos": [
    {
      "account_id": "ACC-10492",
      "kam": "Carlos Mendes",
      "acao_proposta": "Reunião de alinhamento executivo com C-Level e revisão de SLA",
      "status_aprovacao": "pendente"
    }
  ]
}
```

---

## 2. Payload de Resposta HTTP JSON (n8n → Frontend)

Devolvido pelo n8n após a síntese dos agentes para renderização no chat e no painel executivo.

### Schema JSON:
```json
{
  "modelo": "google/gemini-2.5-flash",
  "sessionId": "kovan-sessao-1718000000000",
  "agentes": [
    {
      "nome": "Atlas",
      "papel": "Diagnóstico de Risco",
      "texto": "Identificamos 12 contas em padrão de 'Erosão Silenciosa' no segmento Enterprise. A conta ACC-10492 apresenta probabilidade de churn de 74.2% motivada por queda de 40% na receita e afunilamento de mix de produtos."
    },
    {
      "nome": "Vera",
      "papel": "Saúde do Relacionamento",
      "texto": "Auditoria de CRM indica que a conta ACC-10492 está há 68 dias sem contato proativo registrado. Houve troca de KAM há 4 meses, criando uma zona cega crítica."
    },
    {
      "nome": "Ciro",
      "papel": "Priorização da Fila",
      "texto": "VEREDITO: aprovado\nClassificamos ACC-10492 na posição #1 da fila por Valor Esperado em Risco (EV = R$ 927.500). Alocada para Carlos Mendes (1 de 3 vagas do trimestre utilizadas)."
    },
    {
      "nome": "Diana",
      "papel": "Playbook de Retenção",
      "texto": "Playbook: Resgate Executivo. Minuta pronta gerada para Carlos Mendes agendar workshop executivo em 24h. Alçada comercial: sem concessão de desconto inicial."
    },
    {
      "nome": "Elias",
      "papel": "Mensuração e Aprendizado",
      "texto": "Conta alocada no grupo de intervenção ativa. 2 contas similares foram direcionadas ao grupo de controle holdout. Previsão de impacto: +11.2 pp em Delta NRR."
    }
  ]
}
```

---

## 3. Dicionário de Dados dos Datasets do Projeto

| Dataset | Aba no Excel | Linhas | Colunas Principais | Finalidade |
| :--- | :--- | :--- | :--- | :--- |
| **Dataset 1** | `Dataset 1` | 44.819 | `account_id`, `periodo`, `segment`, `country`, `churn_label`, `receita_usd`, `qtd_pedidos` | Painel temporal de contas e target de churn usado pelo modelo preditivo no frontend. |
| **Dataset 2** | `Dataset 2` | 19.766 | `account_id`, `Brand`, `qtd_skus_distintos`, `pct_receita` | Amplitude de catálogo, profundidade de SKUs e detecção de afunilamento de mix. |
| **Dataset 3** | `Dataset 3` | 89.616 | `account_id`, `periodo`, `contatos_realizados`, `dias_sem_contato`, `oportunidades_abertas`, `oportunidades_ganhas` | Registro de atividade e cadência de engajamento no CRM. |
| **Dataset 4** | `Dataset 4` | 7.260 | `account_id`, `segment`, `industry`, `country`, `tempo_como_cliente`, `canal_aquisicao` | Firmográficos, tempo de relacionamento e canais de entrada. |
| **Compact File** | `datasets_case_modulo2_compact.xlsx` | 161.461 | Contém Datasets 1, 2, 3 e 4 | **Versão otimizada de 4.25 MB** pronta para GitHub e carregamento ultrarrápido. |
