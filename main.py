import os
import json
import pandas as pd
from src.config import REPORTS_DIR, MODELS_DIR, BASE_DIR
from src.data_loader import carregar_dados
from src.feature_engineering import construir_dataset_temporal
from src.models import treinar_modelo, salvar_modelo_joblib
from src.evaluator import simular_impacto_financeiro, gerar_tabela_comparativa_robustez

def main():
    print("=" * 80)
    print(" KOVAN TECHNOLOGIES LATAM — B2B CHURN & SILENT EROSION PREDICTIVE PIPELINE")
    print("=" * 80)

    print("\n[1/5] Loading official datasets (5-Year B2B Sales Data)...")
    data_dict = carregar_dados()

    print("\n[2/5] Constructing temporal dataset (Train: 3 Years [2021-2023] -> Target: Years 4 & 5 [2024-2026])...")
    # Solution B: Silent Erosion
    df_b, feats_b, raw_b = construir_dataset_temporal(
        data_dict=data_dict,
        train_years=[2021, 2022, 2023],
        target_years=[2024, 2025, 2026],
        target_mode="solucao_b",
        erosion_threshold=0.15,
        segment_filter="MID MARKET"
    )

    # Solution A: Rupture Signal (Binary Churn)
    df_a, feats_a, raw_a = construir_dataset_temporal(
        data_dict=data_dict,
        train_years=[2021, 2022, 2023],
        target_years=[2024, 2025, 2026],
        target_mode="solucao_a",
        segment_filter="MID MARKET"
    )

    print(f"      Solution B Dataset ready: {len(df_b)} Mid-Market Accounts.")

    print("\n[3/5] Training ML Models, Optimizing Thresholds & Saving to .joblib...")

    # 1. New Architecture XGBoost (Solution B - Silent Erosion)
    res_xgb_b = treinar_modelo(df_b[feats_b], df_b['target'], algorithm="xgboost", optimize_for="f1")

    # Persist model artifact via joblib
    joblib_path = os.path.join(MODELS_DIR, "kovan_churn_model.joblib")
    salvar_modelo_joblib(res_xgb_b["model"], feats_b, res_xgb_b["metrics"], joblib_path)

    # 2. New Architecture LightGBM (Solution B)
    res_lgb_b = treinar_modelo(df_b[feats_b], df_b['target'], algorithm="lightgbm", optimize_for="f1")

    # 3. Random Forest (Solution B)
    res_rf_b = treinar_modelo(df_b[feats_b], df_b['target'], algorithm="random_forest", optimize_for="f1")

    # 4. XGBoost (Solution A - Rupture)
    res_xgb_a = treinar_modelo(df_a[feats_a], df_a['target'], algorithm="xgboost", optimize_for="f1")

    # Comparative benchmark table
    modelos_dict = {
        "New Architecture (XGBoost — Solution B Silent Erosion)": res_xgb_b,
        "New Architecture (LightGBM — Solution B Silent Erosion)": res_lgb_b,
        "Optimized Random Forest (Solution B Silent Erosion)": res_rf_b,
        "Binary Rupture Model (Solution A Contract Loss)": res_xgb_a,
        "Legacy Baseline (Previous Script)": {
            "metrics": {
                "accuracy": 0.7294,
                "precision": 0.3545,
                "recall": 0.4010,
                "f1_score": 0.3763,
                "roc_auc": 0.6120
            }
        }
    }

    tabela = gerar_tabela_comparativa_robustez(modelos_dict)

    print("\n" + "=" * 80)
    print(" BENCHMARK PERFORMANCE & ROBUSTNESS MATRIX ")
    print("=" * 80)
    print(tabela.to_string(index=False))
    print("=" * 80)

    print("\n[4/5] Simulating Financial Impact & Account Manager Operational Capacity...")
    test_raw_b = raw_b.loc[res_xgb_b["X_test"].index]
    roi_b = simular_impacto_financeiro(
        test_raw_b,
        res_xgb_b["y_probs"],
        threshold=res_xgb_b["metrics"]["optimal_threshold"],
        max_am_capacity=138
    )

    print(f"      - Total Accounts Evaluated in Test: {roi_b['total_contas_analisadas']}")
    print(f"      - Accounts Flagged at Risk: {roi_b['total_contas_sinalizadas']}")
    print(f"      - Accounts Prioritized (138 AM Plans Capacity Ceiling): {roi_b['contas_atendidas_am']}")
    print(f"      - Total Annualized Revenue Flagged at Risk: ${roi_b['receita_total_identificada_usd']:,.2f}")
    print(f"      - Revenue Covered by AM Capacity: ${roi_b['receita_protegida_capacidade_usd']:,.2f}")
    print(f"      - Projected Preserved Revenue (NRR Net Protection): ${roi_b['receita_preservada_nrr_usd']:,.2f}")

    print("\n[5/5] Exporting Static Data Payload for HTML Web Dashboard...")
    # Prepare static payload for direct client-side HTML consumption
    test_df_copy = test_raw_b.copy().reset_index(drop=True)
    test_df_copy['risk_score'] = res_xgb_b["y_probs"]
    test_df_copy['predicted_risk'] = res_xgb_b["y_preds"]

    top_risk_accounts = test_df_copy.sort_values(by=['predicted_risk', 'risk_score', 'rec_fim_train'], ascending=[False, False, False]).head(50)
    
    account_list = []
    for idx, row in top_risk_accounts.iterrows():
        score = float(row['risk_score'])
        status_desc = "Critical Rupture Risk" if score >= 0.75 else ("Silent Revenue Erosion" if score >= 0.45 else "Stable Account")
        action = "Review Mix & Apply Preventive AM Discount" if score >= 0.60 else "Routine Account Retention Contact"
        
        account_list.append({
            "account_id": str(row['account_id']),
            "segment": str(row.get('segment', 'MID MARKET')),
            "country": str(row.get('country', 'LATAM')),
            "receita_atual_usd": float(row.get('rec_fim_train', 0)),
            "pct_servicos": float(row.get('pct_servicos', 0)),
            "pct_hardware": float(row.get('pct_hardware', 0)),
            "dias_sem_contato": float(row.get('dias_sem_contato_medio_obs', 0)),
            "risk_score": float(score),
            "predicted_risk": int(row['predicted_risk']),
            "status": status_desc,
            "recommended_action": action
        })

    benchmark_json = [
        {
            "model": "New Architecture (XGBoost — Solution B)",
            "accuracy": f"{res_xgb_b['metrics']['accuracy']:.2%}",
            "precision": f"{res_xgb_b['metrics']['precision']:.2%}",
            "recall": f"{res_xgb_b['metrics']['recall']:.2%}",
            "f1_score": f"{res_xgb_b['metrics']['f1_score']:.2%}",
            "roc_auc": f"{res_xgb_b['metrics']['roc_auc']:.4f}"
        },
        {
            "model": "Legacy Baseline (Previous Script)",
            "accuracy": "72.94%",
            "precision": "35.45%",
            "recall": "40.10%",
            "f1_score": "37.63%",
            "roc_auc": "0.6120"
        }
    ]

    static_payload = {
        "model_file_name": "kovan_churn_model.joblib",
        "algorithm": "XGBoost (Gradient Boosting)",
        "target_mode": "solucao_b",
        "metrics": res_xgb_b["metrics"],
        "financial_simulation": roi_b,
        "benchmark": benchmark_json,
        "top_features": res_xgb_b["feature_importances"][:10],
        "accounts_at_risk": account_list,
        "params_used": {
            "train_years": [2021, 2022, 2023],
            "target_years": [2024, 2025, 2026],
            "target_mode": "solucao_b",
            "erosion_threshold": 0.15,
            "segment_filter": "MID MARKET",
            "algorithm": "xgboost",
            "decision_threshold": res_xgb_b["metrics"]["optimal_threshold"]
        }
    }

    static_json_path = os.path.join(BASE_DIR, "static", "model_data.json")
    os.makedirs(os.path.dirname(static_json_path), exist_ok=True)
    with open(static_json_path, "w", encoding="utf-8") as f:
        json.dump(static_payload, f, indent=2)

    # Save reports
    os.makedirs(REPORTS_DIR, exist_ok=True)
    tabela.to_csv(os.path.join(REPORTS_DIR, "metricas_robustez.csv"), index=False)
    tabela.to_csv(os.path.join(REPORTS_DIR, "benchmark_comparativo.csv"), index=False)

    print(f"      OK: Model saved to '{joblib_path}'")
    print(f"      OK: Static Web Dashboard Payload saved to '{static_json_path}'")
    print("=" * 80)

if __name__ == "__main__":
    main()
