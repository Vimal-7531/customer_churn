import pandas as pd
import joblib

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, f1_score


DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)


def main():

    print("API MODEL TRAINING")
    print("=" * 60)

    query = """
    SELECT
        tenure,
        monthly_charges,
        contract,
        service_count,
        churn
    FROM customer_ml_features
    """

    df = pd.read_sql(
        query,
        engine
    )

    print("DATA LOADED")
    print("--------------------")
    print("Rows:", len(df))
    print()

    df = pd.get_dummies(
        df,
        columns=["contract"],
        drop_first=False
    )

    X = df.drop(
        columns=["churn"]
    )

    y = df["churn"]

    X = X.astype(float)

    print("FEATURES")
    print("--------------------")
    print(X.columns.tolist())
    print()

    print("FEATURE SHAPE")
    print("--------------------")
    print(X.shape)
    print()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    model = DecisionTreeClassifier(
        max_depth=5,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    print("CLASSIFICATION REPORT")
    print("--------------------")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Active",
                "Churned"
            ]
        )
    )

    print(
        "CHURN F1:",
        f1_score(
            y_test,
            predictions,
            pos_label=1
        )
    )

    joblib.dump(
        model,
        "models/api_churn.pkl"
    )

    joblib.dump(
        X.columns.tolist(),
        "models/api_feature_columns.pkl"
    )

    print()
    print("MODEL SAVED")
    print("--------------------")
    print("models/api_churn.pkl")
    print("models/api_feature_columns.pkl")

    print()
    print("API MODEL COMPLETE")


if __name__ == "__main__":
    main()