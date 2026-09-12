from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from src.config import RANDOM_STATE, TEST_SIZE

def treinar_random_forest(df_modelo, features):
    X = df_modelo[features]
    y = df_modelo['churn_label']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, class_weight='balanced')
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    report = classification_report(y_test, preds, zero_division=0, output_dict=True)
    acc = accuracy_score(y_test, preds)
    return model, acc, report
