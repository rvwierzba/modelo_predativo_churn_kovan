# 🛡️ Sistema Integrado de Prevenção de Churn B2B — Kovan LATAM

> **MBA Executivo em Inteligência Artificial e Dados para Negócios**  
> **Parceria Inteli & Lenovo · Business Case Módulo 2**

---

## 📌 1. Sumário Executivo & Contexto de Negócio

A **Kovan Technologies LATAM** é uma fornecedora líder em tecnologia e infraestrutura B2B na América Latina. No último ano fiscal, a empresa enfrentou uma crise de retenção crítica: sua métrica de **Retenção Líquida de Receita (NRR — *Net Revenue Retention*) despencou de 109% para 93%**.

A investigação interna revelou que a perda de **16 pontos percentuais no NRR** não decorreu de cancelamentos explícitos em massa, mas sim de **contração silenciosa de contas existentes (perda de R$ 248 Milhões)**.

### A Autópsia do Caso *Grupo Talvera*:
O caso mais emblemático foi o do **Grupo Talvera** — cliente que gerava R$ 12 Milhões anuais:
- O CRM mantinha o status da conta como `"Ativa / Risco 0"`.
- As compras eram feitas mecanicamente via portal eletrônico de compras (*Procurement B2B*).
- O volume e o faturamento vinham caindo continuamente por 3 trimestres consecutivos.
- O mix de produtos adquiridos estreitou-se de **6 linhas para apenas 2 linhas**.
- Houve **duas trocas de Gerente de Contas (KAM)** em 10 meses sem registro de reuniões executivas.
- **Resultado:** O cliente cancelou o contrato e migrou para um concorrente sem que qualquer alarme soasse no CRM ou na liderança comercial.

---

## 🚀 2. A Solução: Arquitetura Híbrida de IA & Dados

Para resolver esse desafio com rigor metodológico e viabilidade operacional, o projeto une **Machine Learning Preditivo Client-Side** com um **Ecossistema Multi-Agente Orquestrado via n8n e OpenRouter**:

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                       1. MODELO PREDITIVO CLIENT-SIDE                       │
 │  • Regressão Logística treinada no navegador (5-Fold Cross Validation)      │
 │  • Detecção precoce do padrão de erosão silenciosa com cálculo de AUC e ROC │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                   2. ECOSSISTEMA MULTI-AGENTE (n8n + LLM)                   │
 ├───────────────────┬─────────────────────────────────────────────────────────┤
 │ 🧠 Orquestrador   │ Roteamento semântico, governança HITL e síntese global. │
 │ 📊 Atlas (Ag 1)   │ Diagnóstico de risco e decomposição causal dos scores.  │
 │ 🩺 Vera (Ag 2)    │ Auditoria de CRM, cadência de contato e zonas cegas.    │
 │ 🎯 Ciro (Ag 3)    │ Priorização por Valor Esperado (EV) e teto de 138 vagas.│
 │ 📋 Diana (Ag 4)   │ Playbooks de retenção e minutas acionáveis em até 24h.  │
 │ 📈 Elias (Ag 5)   │ Auditoria financeira de ΔNRR frente ao grupo controle.  │
 └───────────────────┴─────────────────────────────────────────────────────────┘
```

---

## ⚖️ 3. Regras de Ouro e Restrições de Negócio

1. **Teto Operacional Rígido de 138 Vagas/Trimestre:**
   - A Kovan possui **46 Key Account Managers (KAMs)** gerenciando **1.187 contas ativas**.
   - Cada KAM tem capacidade máxima de executar **3 planos de retenção estruturados por trimestre**.
   - **Teto regional = 138 contas**. O agente Ciro **nunca** ultrapassa essa capacidade.
2. **Grupo de Controle Obrigatório (Holdout de 10% a 20%):**
   - Para comprovar ao CFO que a receita preservada decorre das ações de retenção (e não de flutuação natural), uma parcela das contas de risco é mantida sem intervenção ativa.
   - O Agente Elias audita a causalidade via $\Delta\text{NRR} = \text{NRR}_{\text{Intervenção}} - \text{NRR}_{\text{Controle}}$.
3. **Governança Human-In-The-Loop (HITL):**
   - Agentes geram **propostas** e minutas de comunicação.
   - Concessões de margem/desconto $> 10\%$ exigem autorização expressa do Diretor Regional.

---

## 💻 4. Estrutura do Repositório

```
modelo_predativo_churn_kovan/
├── index.html                           # Interface web unificada (Dashboard + Chat + Treinador ML)
├── modelo.js                            # Motor de Regressão Logística 5-Fold CV em JavaScript puro
├── datasets_case_modulo2_compact.xlsx   # Dataset compactado oficial (< 50MB para GitHub: 4.25 MB)
├── workflow_n8n_v2.json                 # Workflow completo do n8n com 26 nós configurados
├── .agents/                             # Documentação técnica e operacional dos Agentes de IA
│   ├── README.md                        # Visão geral do ecossistema de agentes
│   ├── ARCHITECTURE.md                  # Arquitetura detalhada, nós do n8n e OpenRouter
│   ├── ORCHESTRATOR.md                  # Especificação e máquina de estados do Orquestrador
│   ├── ATLAS.md                         # Agente 1: Diagnóstico de Risco
│   ├── VERA.md                          # Agente 2: Saúde do Relacionamento
│   ├── CIRO.md                          # Agente 3: Priorização da Fila & Capacidade (138)
│   ├── DIANA.md                         # Agente 4: Playbooks de Retenção
│   ├── ELIAS.md                         # Agente 5: Mensuração, Auditoria & Aprendizado
│   └── DATA_CONTRACTS.md                # Schemas JSON de integração Frontend ↔ n8n
└── README.md                            # Documentação principal do projeto
```

---

## 🛠️ 5. Como Executar o Projeto

### Passo 1: Abrir a Interface Web
Abra o arquivo [`index.html`](./index.html) em qualquer navegador moderno (Chrome, Edge, Firefox, Safari). Não requer servidor Node.js ou build complexo.

### Passo 2: Carregar a Base de Dados
No **Bloco 01**, clique em *Carregar Planilha* e selecione o arquivo otimizado [`datasets_case_modulo2_compact.xlsx`](./datasets_case_modulo2_compact.xlsx).
- O motor `modelo.js` executará o treinamento da Regressão Logística com 5-Fold Cross Validation em tempo real.
- As métricas de AUC-ROC, Acurácia, F1-Score, Sensibilidade e Especificidade serão exibidas instantaneamente.

### Passo 3: Conectar com o n8n
1. Importe o arquivo [`workflow_n8n_v2.json`](./workflow_n8n_v2.json) em sua instância do [n8n](https://n8n.io/).
2. Configure sua credencial da [OpenRouter](https://openrouter.ai/) nos nós de modelo de linguagem.
3. Ative o workflow no n8n e copie a URL de Produção do Webhook.
4. No **Bloco 03** do `index.html`, cole a URL do webhook e clique em **Testar Conexão**.

### Passo 4: Interagir com a Equipe Multi-Agente
No **Bloco 04 (Conversa com a equipe)**, envie suas consultas executivas:
- O painel exibirá em tempo real o **indicador visual luminoso do agente ativo**, a digitação com cursor dinâmico e o carimbo de veredito de aprovação.
- As respostas de cada especialista serão sincronizadas automaticamente com as abas do **Painel Executivo da Diretoria**.

---

## 📊 6. Datasets do Projeto

O arquivo [`datasets_case_modulo2_compact.xlsx`](./datasets_case_modulo2_compact.xlsx) (4.25 MB) consolida as 4 bases estruturadas do Case:

| Dataset | Registros | Descrição |
| :--- | :---: | :--- |
| **Dataset 1** | 44.819 | Painel trimestral de contas com histórico de faturamento e target de churn. |
| **Dataset 2** | 19.766 | Abertura de mix de produtos, marcas e contagem de SKUs ativos. |
| **Dataset 3** | 89.616 | Telemetria de CRM, dias sem contato e histórico de oportunidades. |
| **Dataset 4** | 7.260 | Dados cadastrais, setor da indústria e tempo de relacionamento. |

---

## 🎓 7. Créditos Acadêmicos

- **Instituição:** Inteli &mdash; Instituto de Tecnologia e Liderança
- **Programa:** MBA Executivo em IA e Dados para Negócios
- **Parceiro Corporativo:** Lenovo LATAM
- **Disciplina:** Módulo 2 &mdash; Modelagem Preditiva e Agentes Autônomos de Decisão
