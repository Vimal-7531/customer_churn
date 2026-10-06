import pandas as pd
import joblib

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)

def load_and_prepare_data():

    query = """
    SELECT *
    FROM customer_ml_features
    """

    df = pd.read_sql(query, engine)

    print("DATA LOADED")
    print("--------------------")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print()

    df["service_count"] = pd.to_numeric(
        df["service_count"],
        errors="coerce"
    )

    X = df.drop(columns=["customer_id", "churn"])
    y = df["churn"]

    categorical_columns = [
        "gender",
        "multiple_lines",
        "internet_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
        "contract",
        "payment_method",
        "tenure_bucket"
    ]

    print("CATEGORICAL COLUMNS TO ENCODE")
    print("--------------------")
    print(categorical_columns)
    print()

    X = pd.get_dummies(
        X,
        columns=categorical_columns,
        drop_first=False
    )

    X = X.astype(float)

    print("FINAL FEATURE SHAPE")
    print("--------------------")
    print(X.shape)
    print()

    print("TARGET SHAPE")
    print("--------------------")
    print(y.shape)
    print()

    return X, y


def train_models(X_train, y_train):

    logistic_model = LogisticRegression(
        max_iter=1000
    )

    tree_model = DecisionTreeClassifier(
        max_depth=5,
        random_state=42
    )

    logistic_model.fit(X_train, y_train)

    tree_model.fit(X_train, y_train)

    return logistic_model, tree_model


def evaluate_model(model, X_test, y_test, model_name):

    predictions = model.predict(X_test)

    print()
    print("=" * 60)
    print(model_name)
    print("=" * 60)

    print()
    print("CLASSIFICATION REPORT")
    print("--------------------")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=["Active", "Churned"]
        )
    )

    print("CONFUSION MATRIX")
    print("--------------------")

    cm = confusion_matrix(
        y_test,
        predictions
    )

    print(cm)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        pos_label=1
    )

    recall = recall_score(
        y_test,
        predictions,
        pos_label=1
    )

    f1 = f1_score(
        y_test,
        predictions,
        pos_label=1
    )

    return {
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision (Churned)": precision,
        "Recall (Churned)": recall,
        "F1 (Churned)": f1
    }


def calculate_cv_f1(model, X_train, y_train):

    scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=5,
        scoring="f1"
    )

    print("CV F1 SCORES")
    print("--------------------")
    print(scores)

    print("Mean CV F1:", scores.mean())
    print()

    return scores.mean()


def main():

    print("ML2 - BUILD AND COMPARE BASELINE MODELS")
    print("=" * 60)
    print()

    X, y = load_and_prepare_data()

    print("SPLITTING DATA")
    print("--------------------")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print("Training rows:", len(X_train))
    print("Testing rows:", len(X_test))
    print()

    logistic_model, tree_model = train_models(
        X_train,
        y_train
    )

    logistic_results = evaluate_model(
        logistic_model,
        X_test,
        y_test,
        "LOGISTIC REGRESSION"
    )

    logistic_cv_f1 = calculate_cv_f1(
        logistic_model,
        X_train,
        y_train
    )

    logistic_results["CV F1"] = logistic_cv_f1

    tree_results = evaluate_model(
        tree_model,
        X_test,
        y_test,
        "DECISION TREE"
    )

    tree_cv_f1 = calculate_cv_f1(
        tree_model,
        X_train,
        y_train
    )

    tree_results["CV F1"] = tree_cv_f1

    comparison = pd.DataFrame(
        [
            logistic_results,
            tree_results
        ]
    )

    print()
    print("=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)

    print(
        comparison.to_string(
            index=False
        )
    )

    print()
    print("=" * 60)
    print("MODEL SELECTION")
    print("=" * 60)

    logistic_f1 = logistic_results["F1 (Churned)"]
    tree_f1 = tree_results["F1 (Churned)"]

    if logistic_f1 > tree_f1:
        print(
            "Logistic Regression is selected because it has "
            "the higher F1 score for the Churned class."
        )
    elif tree_f1 > logistic_f1:
        print(
            "Decision Tree is selected because it has "
            "the higher F1 score for the Churned class."
        )
    else:
        print(
            "Both models have the same F1 score for the "
            "Churned class."
        )

    print()
    print("SAVING MODELS")
    print("--------------------")

    joblib.dump(
        logistic_model,
        "models/logistic_churn.pkl"
    )

    joblib.dump(
        tree_model,
        "models/tree_churn.pkl"
    )

    print("Saved: models/logistic_churn.pkl")
    print("Saved: models/tree_churn.pkl")

    print()
    print("ML2 COMPLETE")


if __name__ == "__main__":
    main()