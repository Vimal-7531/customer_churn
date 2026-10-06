import pandas as pd
import joblib

from sqlalchemy import create_engine


DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)

MODEL_FILE = "models/tree_churn.pkl"


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

    customer_ids = df["customer_id"].copy()

    X = df.drop(
        columns=["customer_id", "churn"]
    )

    y = df["churn"]

    categorical_columns = X.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

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

    return X, y, customer_ids


def load_model():

    model = joblib.load(
        MODEL_FILE
    )

    print("MODEL LOADED")
    print("--------------------")
    print("Decision Tree model loaded")
    print()

    return model


def split_data(X, y, customer_ids):

    from sklearn.model_selection import train_test_split

    (
        X_train,
        X_test,
        y_train,
        y_test,
        id_train,
        id_test
    ) = train_test_split(
        X,
        y,
        customer_ids,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print("DATA SPLIT")
    print("--------------------")
    print("Training rows:", len(X_train))
    print("Testing rows:", len(X_test))
    print()

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        id_train,
        id_test
    )


def feature_importance(model, X_train):

    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    )

    print("=" * 60)
    print("TOP 10 FEATURE IMPORTANCE")
    print("=" * 60)

    print(
        importance_df.head(10).to_string(
            index=False
        )
    )

    print()

    print("TOP 3 FEATURES")
    print("--------------------")

    for index, row in importance_df.head(3).iterrows():

        print(
            f"{row['feature']}: "
            f"{row['importance']:.6f}"
        )

    print()

    return importance_df

def plot_feature_importance(importance_df):

    import matplotlib.pyplot as plt

    top_10 = importance_df.head(10).sort_values(
        by="importance"
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        top_10["feature"],
        top_10["importance"]
    )

    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Top 10 Decision Tree Feature Importance")

    plt.tight_layout()

    plt.show()

def calculate_risk_scores(
    model,
    X_test,
    id_test
):

    risk_scores = model.predict_proba(
        X_test
    )[:, 1]

    risk_df = pd.DataFrame({
        "customer_id": id_test.values,
        "risk_score": risk_scores
    })

    risk_df = risk_df.sort_values(
        by="risk_score",
        ascending=False
    )

    top_20 = risk_df.head(20)

    print("=" * 60)
    print("TOP 20 HIGHEST-RISK CUSTOMERS")
    print("=" * 60)

    print(
        top_20.to_string(
            index=False
        )
    )

    print()

    return top_20


def compare_with_sql6(top_20):

    print("=" * 60)
    print("SQL6 OVERLAP ANALYSIS")
    print("=" * 60)

    try:

        query = """
        SELECT customer_id
        FROM v_high_risk_customers
        """

        sql6_df = pd.read_sql(
            query,
            engine
        )

        ml_customers = set(
            top_20["customer_id"].astype(str)
        )

        sql6_customers = set(
            sql6_df["customer_id"].astype(str)
        )

        overlap = (
            ml_customers
            .intersection(sql6_customers)
        )

        print(
            "ML top-20 customers:",
            len(ml_customers)
        )

        print(
            "SQL6 high-risk customers:",
            len(sql6_customers)
        )

        print(
            "Customers appearing in both:",
            len(overlap)
        )

        print(
            "Overlap:",
            f"{len(overlap)}/20"
        )

        print()

        if len(overlap) > 0:

            print("OVERLAPPING CUSTOMERS")
            print("--------------------")

            for customer_id in sorted(overlap):

                print(customer_id)

        else:

            print(
                "No overlap found."
            )

    except Exception as e:

        print(
            "Could not query SQL6 high-risk view."
        )

        print(
            "Error:",
            e
        )

    print()


def business_interpretation(
    importance_df
):

    top_features = (
        importance_df
        .head(3)["feature"]
        .tolist()
    )

    print("=" * 60)
    print("BUSINESS INTERPRETATION")
    print("=" * 60)

    print(
        "1. Customers whose characteristics match "
        "the strongest model features should receive "
        "greater retention attention."
    )

    print(
        "2. Short-tenure customers are important "
        "candidates for proactive retention campaigns "
        "when tenure appears among the leading features."
    )

    print(
        "3. Customers with month-to-month contracts "
        "should receive additional attention because "
        "contract type is a known churn-related factor."
    )

    print(
        "4. Customers with high predicted churn "
        "probabilities should be contacted before "
        "they decide to leave."
    )

    print(
        "5. The retention team should combine the "
        "model's risk scores with business rules to "
        "prioritize customers for targeted offers."
    )

    print()

    print("ACTUAL TOP 3 MODEL FEATURES")
    print("--------------------")

    for feature in top_features:

        print(feature)

    print()


def main():

    print("=" * 60)
    print("ML3 - INTERPRET MODEL BEHAVIOUR")
    print("=" * 60)
    print()

    X, y, customer_ids = (
        load_and_prepare_data()
    )

    model = load_model()

    (
        X_train,
        X_test,
        y_train,
        y_test,
        id_train,
        id_test
    ) = split_data(
        X,
        y,
        customer_ids
    )

    importance_df = feature_importance(
        model,
        X_train
    )
    plot_feature_importance(
    importance_df
    )

    top_20 = calculate_risk_scores(
        model,
        X_test,
        id_test
    )

    compare_with_sql6(
        top_20
    )

    business_interpretation(
        importance_df
    )

    print("=" * 60)
    print("ML3 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()