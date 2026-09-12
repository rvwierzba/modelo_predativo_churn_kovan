import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# =================================================================
# 1. CARREGAMENTO DAS ABAS CORRETAS
# =================================================================
caminho_excel = 'data/datasets_case_modulo2_5yrs.xlsx'
print(f"Lendo dados de '{caminho_excel}'...")

try:
    # Nomes exatos com espaços
    df_raw = pd.read_excel(caminho_excel, sheet_name='raw data')
    df_portfolio = pd.read_excel(caminho_excel, sheet_name='Dataset 2')
    print("Abas 'raw data' e 'Dataset 2' carregadas com sucesso!")
except Exception as e:
    print(f"Erro ao carregar o arquivo Excel: {e}")
    exit()

# =================================================================
# 2. ENGENHARIA DE FEATURES (CAMINHO B: SERVIÇOS VS HARDWARE)
# =================================================================
print("\nProcessando agregações e engenharia de atributos...")

# Limpeza dos nomes de colunas
df_raw.columns = df_raw.columns.str.strip()
df_portfolio.columns = df_portfolio.columns.str.strip()

# Agregação temporal por conta e trimestre
df_agg = df_raw.groupby(['account_id', 'quarter', 'segment']).agg(
    receita_total=('total_value_usd', 'sum'),
    qtde_pedidos=('invoice_no', 'nunique'),
    churn_label=('churn_label', 'first')
).reset_index()

# Percentual de receita de serviços a partir do 'Dataset 2'
df_servicos = df_portfolio[df_portfolio['Brand'] == 'SERVICES'][['account_id', 'pct_receita']]
df_servicos = df_servicos.rename(columns={'pct_receita': 'pct_receita_servicos'})

# Junção das bases
df_final = pd.merge(df_agg, df_servicos, on='account_id', how='left')
df_final['pct_receita_servicos'] = df_final['pct_receita_servicos'].fillna(0)
df_final['foco_em_servicos'] = (df_final['pct_receita_servicos'] > 0.9).astype(int)

# =================================================================
# 3. FILTRO DO SEGMENTO MID-MARKET
# =================================================================
df_modelo = df_final[df_final['segment'] == 'MID MARKET'].copy()
print(f"Registros prontos para treino e teste (Mid-Market): {len(df_modelo)}")

# =================================================================
# 4. TREINAMENTO DO MODELO
# =================================================================
features = ['receita_total', 'qtde_pedidos', 'pct_receita_servicos', 'foco_em_servicos']
X = df_modelo[features]
y = df_modelo['churn_label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# =================================================================
# 5. AVALIAÇÃO DE RESULTADOS
# =================================================================
predictions = model.predict(X_test)

print(f"\nAcurácia Geral: {accuracy_score(y_test, predictions):.2%}")
print("\n--- Relatório de Classificação ---")
print(classification_report(y_test, predictions, zero_division=0))

importancias = pd.DataFrame({
    'feature': features,
    'importancia': model.feature_importances_
}).sort_values('importancia', ascending=False)

print("--- Importância dos Atributos no Modelo ---")
print(importancias.to_string(index=False))
