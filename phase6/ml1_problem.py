import pandas as pd
from sqlalchemy import create_engine


DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)


def load_data():
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

    return df


def prepare_data(df):

    print("ORIGINAL COLUMNS")
    print("--------------------")
    print(df.columns.tolist())
    print()

    target = "churn"

    drop_columns = ["customer_id"]

    numeric_columns = [
        "tenure",
        "monthly_charges",
        "total_charges",
        "service_count",
        "high_charge_flag",
        "is_long_term_customer",
        "auto_pay_flag",
        "has_streaming_bundle"
    ]

    categorical_columns = [
        "contract",
        "internet_service"
    ]

    print("TARGET")
    print("--------------------")
    print(target)
    print()

    print("COLUMNS TO DROP")
    print("--------------------")
    print(drop_columns)
    print()

    print("NUMERIC COLUMNS")
    print("--------------------")
    print(numeric_columns)
    print()

    print("CATEGORICAL COLUMNS")
    print("--------------------")
    print(categorical_columns)
    print()

    X = df.drop(columns=[target] + drop_columns)

    y = df[target]

    X = pd.get_dummies(
        X,
        columns=categorical_columns,
        drop_first=False
    )

    print("FINAL FEATURE SET")
    print("--------------------")
    print(X.columns.tolist())
    print()

    print("X")
    print("--------------------")
    print(X.head())
    print()

    print("TARGET y")
    print("--------------------")
    print(y.head())
    print()

    print("SHAPES")
    print("--------------------")
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    print()

    print("CLASS BALANCE")
    print("--------------------")
    print(y.value_counts(normalize=True))
    print()

    print("CLASS COUNTS")
    print("--------------------")
    print(y.value_counts())
    print()

    return X, y


def main():

    print("ML1 - DEFINE ML PROBLEM")
    print("============================")
    print()

    df = load_data()

    X, y = prepare_data(df)

    print("ML1 COMPLETE")
    print("============================")


if __name__ == "__main__":
    main()