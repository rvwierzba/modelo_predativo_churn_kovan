import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from src.config import RANDOM_STATE, MODELS_DIR

def treinar_modelo(
    X, y,
    algorithm="xgboost",
    test_size=0.30,
    decision_threshold=None,
    optimize_for="f1"
):
    """
    Treina modelo supervisionado de ML com balanceamento e otimização de limiar de decisão.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y
    )

    pos_scale = (len(y_train) - sum(y_train)) / max(sum(y_train), 1)

    if algorithm == "xgboost":
        model = XGBClassifier(
            n_estimators=350,
            max_depth=5,
            learning_rate=0.03,
            scale_pos_weight=pos_scale,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1
        )
    elif algorithm == "lightgbm":
        model = LGBMClassifier(
            n_estimators=350,
            max_depth=6,
            num_leaves=45,
            learning_rate=0.03,
            scale_pos_weight=pos_scale,
            random_state=RANDOM_STATE,
            verbose=-1,
            n_jobs=-1
        )
    elif algorithm == "gradient_boosting":
        model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            random_state=RANDOM_STATE
        )
    else: # random_forest
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        )

    model.fit(X_train, y_train)

    y_probs = model.predict_proba(X_test)[:, 1]
    auc_score = roc_auc_score(y_test, y_probs)

    if decision_threshold is None:
        best_t = 0.50
        best_metric_val = 0.0
        for t in np.arange(0.15, 0.85, 0.02):
            preds_t = (y_probs >= t).astype(int)
            p = precision_score(y_test, preds_t, zero_division=0)
            r = recall_score(y_test, preds_t, zero_division=0)
            f1 = f1_score(y_test, preds_t, zero_division=0)

            val = f1 if optimize_for == "f1" else r
            if val > best_metric_val:
                best_metric_val = val
                best_t = t
        optimal_threshold = float(best_t)
    else:
        optimal_threshold = float(decision_threshold)

    y_preds = (y_probs >= optimal_threshold).astype(int)

    acc = accuracy_score(y_test, y_preds)
    prec = precision_score(y_test, y_preds, zero_division=0)
    rec = recall_score(y_test, y_preds, zero_division=0)
    f1 = f1_score(y_test, y_preds, zero_division=0)
    cm = confusion_matrix(y_test, y_preds).tolist()

    if hasattr(model, "feature_importances_"):
        importances = pd.DataFrame({
            "feature": X.columns,
            "importance": model.feature_importances_
        }).sort_values("importance", ascending=False).to_dict(orient="records")
    else:
        importances = []

    metrics = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "roc_auc": float(auc_score),
        "optimal_threshold": float(optimal_threshold),
        "confusion_matrix": cm,
        "test_samples": len(y_test),
        "train_samples": len(y_train)
    }

    return {
        "model": model,
        "metrics": metrics,
        "feature_importances": importances,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "y_probs": y_probs,
        "y_preds": y_preds
    }

def salvar_modelo_joblib(model_obj, feature_cols, metrics, filepath=None):
    """
    Salva o modelo treinado e metadados associados em formato .joblib.
    """
    if filepath is None:
        os.makedirs(MODELS_DIR, exist_ok=True)
        filepath = os.path.join(MODELS_DIR, "kovan_churn_model.joblib")
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    payload = {
        "model": model_obj,
        "feature_cols": list(feature_cols),
        "metrics": metrics,
        "saved_at": pd.Timestamp.now().isoformat()
    }
    
    joblib.dump(payload, filepath)
    print(f"[ModelPersist] Modelo salvo com sucesso em: '{filepath}'")
    return filepath

def carregar_modelo_joblib(filepath=None):
    """
    Carrega o modelo e metadados persistidos via joblib.
    """
    if filepath is None:
        filepath = os.path.join(MODELS_DIR, "kovan_churn_model.joblib")
        
    if not os.path.exists(filepath):
        return None
        
    payload = joblib.load(filepath)
    print(f"[ModelPersist] Modelo .joblib carregado com sucesso de: '{filepath}'")
    return payload
