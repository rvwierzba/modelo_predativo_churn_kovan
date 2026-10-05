# 🤖 Sistema Multi-Agente de Retenção — Kovan LATAM

> **Documentação dos Agentes Inteligentes de Prevenção e Combate ao Churn B2B**  
> **MBA em IA e Dados para Negócios &middot; Inteli x Lenovo &middot; Módulo 2**

---

## 🎯 1. Visão Geral do Ecossistema

O sistema multi-agente foi concebido para resolver o dilema crítico de **retenção de clientes B2B Enterprise** na **Kovan Technologies LATAM**. O ecossistema opera sobre uma arquitetura orquestrada que combina **Machine Learning preditivo client-side** (Regressão Logística com 5-Fold Cross Validation no navegador) com **5 Agentes Especializados em LLM** via **n8n e OpenRouter**.

```
                ┌──────────────────────────────────────────────┐
                │             Interface do Usuário             │
                │        (index.html + modelo.js)              │
                │   • Treinamento LR 5-Fold no Navegador       │
                │   • Scoring de Risco em Tempo Real           │
                └──────────────────────┬───────────────────────┘
                                       │ HTTP POST (Webhook)
                                       ▼
                ┌──────────────────────────────────────────────┐
                │          Orquestrador (Router / HITL)        │
                │   • Validação de Payload & Filtro de Entrada │
                │   • Classificador de Roteamento Semântico    │
                │   • Máquina de Estados Human-In-The-Loop     │
                └──────┬──────────┬──────────┬──────────┬──────┘
                       │          │          │          │
        ┌──────────────┘          │          │          └──────────────┐
        ▼                         ▼          ▼                         ▼
┌───────────────┐         ┌───────────────┐  ┌───────────────┐ ┌───────────────┐
│     ATLAS     │         │     VERA      │  │     CIRO      │ │     DIANA     │
│ Agente 1:     │         │ Agente 2:     │  │ Agente 3:     │ │ Agente 4:     │
│ Diagnóstico   │         │ Saúde do      │  │ Priorização   │ │ Playbook de   │
│ de Risco      │         │ Relacionamento│  │ da Fila (138) │ │ Retenção      │
└───────┬───────┘         └───────┬───────┘  └───────┬───────┘ └───────┬───────┘
        │                         │                  │                 │
        └─────────────────────────┼──────────────────┴─────────────────┘
                                  ▼
                ┌──────────────────────────────────────────────┐
                │                    ELIAS                     │
                │ Agente 5: Mensuração, Auditoria & Aprendizado│
                │   • Delta NRR (Intervenção vs Controle)      │
                │   • Calibração de Thresholds & Drift         │
                └──────────────────────────────────────────────┘
```

---

## 👥 2. Quadro de Agentes Especialistas

| Agente | Papel Executivo | Missão Principal | Cor Tema | Ícone |
| :--- | :--- | :--- | :---: | :---: |
| **Orquestrador** | Roteador & Gatekeeper HITL | Valida entradas, direciona intents para os agentes certos, impõe aprovações humanas e sintetiza as respostas. | `--seg-primaria` | `hub` |
| **Atlas** | Diagnóstico de Risco | Decompor a probabilidade estatística de churn em 4 padrões de risco causais e fatores explicativos. | `#0084FF` | `analytics` |
| **Vera** | Saúde do Relacionamento | Cruzar dados transacionais do ERP com cadência de CRM, identificando zonas cegas e risco de morte súbita. | `#00B87C` | `health_and_safety` |
| **Ciro** | Priorização da Fila | Classificar as contas elegíveis dentro do teto operacional estrito de **138 vagas/trimestre** por Valor Esperado (EV). | `#E2231A` | `sort` |
| **Diana** | Playbook de Retenção | Elaborar planos de ação acionáveis em até 18-24h com táticas multi-departamentais prontas para aprovação. | `#7B2CBF` | `menu_book` |
| **Elias** | Mensuração & Auditoria | Auditar o impacto financeiro (North Star: $\Delta\text{NRR}$ frente ao grupo de controle), monitorar drift e emitir recomendação *Go/Adjust/Stop*. | `#00B4D8` | `insights` |

---

## 📂 3. Estrutura da Documentação

Aprofunde-se na documentação específica de cada módulo:

1. [**Arquitetura do Sistema e n8n**](./ARCHITECTURE.md) — Fluxo de dados, nós do n8n, modelo de dados, OpenRouter e tratamento de erros.
2. [**Agente Orquestrador**](./ORCHESTRATOR.md) — Roteamento dinâmico, classificação de intenções e máquina de estados HITL (*Human-In-The-Loop*).
3. [**Agente Atlas**](./ATLAS.md) — Diagnóstico preditivo, decomposição de risco e identificação do padrão Talvera.
4. [**Agente Vera**](./VERA.md) — Matriz de cobertura CRM, detecção de portais de compras e desengajamento executivo.
5. [**Agente Ciro**](./CIRO.md) — Algoritmo de ranking por Valor Esperado, teto de 138 contas e isolamento de grupo de controle.
6. [**Agente Diana**](./DIANA.md) — Geração de playbooks, limites de autonomia comercial e minutas pré-formatadas para KAMs.
7. [**Agente Elias**](./ELIAS.md) — Auditoria financeira de NRR, metodologia de A/B holdout e governança algorítmica.
8. [**Contratos de Dados e Schemas**](./DATA_CONTRACTS.md) — Especificações de JSON de entrada e saída consumidos e gerados no webhook.

---

## 🔒 4. Princípios de Governança e Regras de Ouro

1. **Restrição de Capacidade Operacional (Hard Limit):**
   - 46 Key Account Managers (KAMs) na América Latina.
   - Cada KAM tem capacidade máxima de executar **3 planos estruturados de retenção por trimestre**.
   - **Teto regional absoluto = 138 contas/trimestre**. O agente Ciro **nunca** pode exceder 138 recomendações ativas.

2. **Grupo de Controle Obrigatório (Holdout):**
   - Para toda coorte de contas priorizadas, **10% a 20% das contas elegíveis devem ser mantidas em grupo de controle puro** (sem intervenção de retenção proativa).
   - Isso permite que o Agente Elias comprove ao Diretor Financeiro (CFO) a causalidade da recuperação de receita via $\Delta\text{NRR} = \text{NRR}_{\text{intervenção}} - \text{NRR}_{\text{controle}}$.

3. **Governança Human-In-The-Loop (HITL):**
   - Agentes operam primariamente em modo **proposta**.
   - Qualquer concessão comercial de margem > 10%, alteração de SLA em contrato ou repactuação exige aprovação explícita do Diretor Regional / Gerente de Contas.

