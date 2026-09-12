from src.data_loader import carregar_dados
from src.feature_engineering import construir_features
from src.time_series_models import executar_sarima_receita
from src.robustness_tests import executar_estudo_robustez

def main():
    print("=" * 80)
    print("EXECUTANDO PIPELINE COMPLETO - MODELO PREDITIVO DE CHURN KOVAN")
    print("=" * 80)

    print("\n[1/4] Carregando dados oficiais do Excel...")
    df_raw, df_portfolio = carregar_dados()
    print(f"      OK: {len(df_raw)} transações brutas.")

    print("\n[2/4] Executando engenharia de features (Segmento Mid-Market)...")
    df_mid = construir_features(df_raw, df_portfolio)
    print(f"      OK: {len(df_mid)} registros prontos para modelagem.")

    print("\n[3/4] Ajustando modelo SARIMA para receita agregada...")
    _, _, forecast = executar_sarima_receita(df_raw)
    print(f"      Previsões SARIMA:\n{forecast.to_string()}")

    print("\n[4/4] Executando testes de robustez e gerando tabela de métricas...")
    tabela = executar_estudo_robustez(df_mid)
    
    print("\n" + "=" * 80)
    print("RESULTADOS DO ESTUDO DE ROBUSTEZ DE FEATURES")
    print("=" * 80)
    print(tabela.to_string(index=False))
    print("=" * 80)
    print("\nRelatório salvo em 'reports/metricas_robustez.csv'")

if __name__ == "__main__":
    main()
