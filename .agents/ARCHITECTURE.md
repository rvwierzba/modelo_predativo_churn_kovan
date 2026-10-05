# 🏗️ Arquitetura Técnica do Sistema Multi-Agente

> **Documentação de Engenharia e Integração n8n**  
> **Kovan LATAM &middot; MBA Inteli x Lenovo**

---

## 1. Topologia da Arquitetura

O sistema integra três camadas principais:

```
[ Camada 1: Client / Web Frontend ]
   • index.html (UI Executiva + Chat Conversacional)
   • modelo.js (Regressão Logística 5-Fold CV em JavaScript)
   • SheetJS (Processamento de planilhas Excel Dataset 1-4)
            │
            │ HTTP POST (Payload JSON com sessionId, modelo, contas, planos)
            ▼
[ Camada 2: Orquestrador n8n (Workflow Workflow_n8n_v2.json) ]
   • Webhook Receiver & Input Sanitizer (JavaScript)
   • Human-In-The-Loop Approval Parser & State Evaluator
   • Semantic Intent Switch (Roteamento Dinâmico)
   • OpenRouter Model Router (Llama-3, Claude 3.5 Sonnet, GPT-4o)
   • Aggregator & Response Formatter
            │
            │ HTTP JSON Response
            ▼
[ Camada 3: Execução dos Agentes de IA ]
   • Atlas (Diagnóstico de Risco)
   • Vera (Saúde do Relacionamento)
   • Ciro (Priorização e Teto de 138)
   • Diana (Playbook de Retenção)
   • Elias (Mensuração de Delta NRR)
```

---

## 2. Nós do Workflow n8n (`workflow_n8n_v2.json`)

O workflow é composto por 26 nós interligados:

### A. Camada de Ingestão e Sanitização
1. **`Webhook Ingestão`** (`n8n-nodes-base.webhook`):
   - Método: `POST`
   - Path: `/webhook/kovan-churn-agents`
   - Autenticação: Configurável (Header Auth ou Pública)
2. **`Input Sanitizer & Context Builder`** (`n8n-nodes-base.code`):
   - Valida os campos obrigatórios (`pergunta`, `modelo`, `contas`).
   - Normaliza os dados dos 4 datasets para o formato tabular esperado pelas LLMs.
   - Extrai as top 10 contas de maior risco da sessão.

### B. Camada de Decisão e Roteamento
3. **`HITL Approval Check`** (`n8n-nodes-base.if`):
   - Verifica se a mensagem contém comandos de aprovação/rejeição humana (ex: `"APROVAR_FILA"`, `"APROVAR_PLANO_CONTA_104"`, `"REJEITAR_PLANO"`).
   - Se aprovado, altera o estado interno da sessão e direciona para o agente subsequente.
4. **`Intent Classifier (Orquestrador)`** (`@n8n/n8n-nodes-langchain.agent`):
   - Determina se a pergunta deve ser respondida por:
     - `atlas_only` (dúvidas sobre cálculo de probabilidade, AUC, curva ROC, churn Talvera)
     - `vera_only` (dúvidas de relacionamento no CRM, visitas, NPS, portais)
     - `ciro_only` (fila de priorização, limite de 138 contas, alocação por KAM)
     - `diana_only` (elaboração ou revisão de planos de ação, minutas para executivos)
     - `elias_only` (mensuração de impacto, delta NRR, auditoria de controle)
     - `pipeline_completo` (análise ponta a ponta com Atlas -> Vera -> Ciro -> Diana -> Elias)

### C. Camada de Modelos de Linguagem (OpenRouter)
5. **`OpenRouter Model Provider`** (`@n8n/n8n-nodes-langchain.lmChatOpenAi`):
   - Base URL: `https://openrouter.ai/api/v1`
   - Modelos suportados dinamicamente via parâmetro `modelo_llm`:
     - `google/gemini-2.5-flash` (Padrão: Alta velocidade e precisão)
     - `meta-llama/llama-3.3-70b-instruct` (Alta capacidade de raciocínio lógico)
     - `anthropic/claude-3.5-sonnet` (Síntese executiva avançada)
     - `openai/gpt-4o` (Análise quantitativa)

### D. Camada de Agregação e Resposta
6. **`Synthesizer & Format Normalizer`** (`n8n-nodes-base.code`):
   - Formata a saída no padrão consumido pelo chat:
   ```json
   {
     "modelo": "google/gemini-2.5-flash",
     "agentes": [
       { "nome": "Atlas", "papel": "Diagnóstico de Risco", "texto": "..." },
       { "nome": "Vera", "papel": "Saúde do Relacionamento", "texto": "..." },
       { "nome": "Ciro", "papel": "Priorização da Fila", "texto": "..." },
       { "nome": "Diana", "papel": "Playbook de Retenção", "texto": "..." },
       { "nome": "Elias", "papel": "Mensuração e Aprendizado", "texto": "..." }
     ]
   }
   ```

---

## 3. Máquina de Estados Human-In-The-Loop (HITL)

O sistema implementa 3 portões de validação (*Approval Gates*):

### Regras dos Portões de Aprovação:
1. **Gate 1 - Validação da Fila (Ciro):** O gestor comercial deve aprovar a lista antes do disparo de planos. Contas estratégicas que não podem receber desconto devem ser marcadas.
2. **Gate 2 - Validação Comercial do Plano (Diana):** Planos com concessão de desconto > 10% ou renegociação de prazo de pagamento exigem chancela do Diretor Financeiro/Regional.
3. **Gate 3 - Auditoria de Eficácia (Elias):** Se $\Delta\text{NRR} < 0$ após 60 dias, o comitê executivo decide entre calibrar os playbooks (*Adjust*) ou interromper as táticas ineficazes (*Stop*).
