import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

from predict import predict_churn


DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)


def load_customers():

    query = """
    SELECT
        customer_id,
        tenure,
        monthly_charges,
        contract,
        service_count
    FROM customer_ml_features
    """

    df = pd.read_sql(query, engine)

    df = df.rename(
        columns={
            "contract": "contract_type"
        }
    )

    print("CUSTOMERS LOADED")
    print("--------------------")
    print("Rows:", len(df))
    print()

    return df


def score_customer(row):

    result = predict_churn(
        tenure=int(row["tenure"]),
        monthly_charges=float(row["monthly_charges"]),
        contract_type=row["contract_type"],
        service_count=int(row["service_count"])
    )

    return pd.Series(
        {
            "risk_score": result["risk_score"],
            "prediction": result["prediction"],
            "confidence": result["confidence"]
        }
    )


def build_risk_table(df):

    print("SCORING CUSTOMERS")
    print("--------------------")

    scores = df.apply(
        score_customer,
        axis=1
    )

    result = pd.concat(
        [
            df[["customer_id"]],
            scores
        ],
        axis=1
    )

    result["scoring_date"] = datetime.today().strftime(
        "%Y-%m-%d"
    )

    return result


def save_risk_table(df):

    df.to_sql(
        "customer_risk_table",
        engine,
        if_exists="replace",
        index=False
    )

    print()
    print("RISK TABLE SAVED")
    print("--------------------")
    print("Rows:", len(df))
    print()


def print_summary(df):

    print("PREDICTION SUMMARY")
    print("--------------------")

    summary = df["prediction"].value_counts()

    print(summary)
    print()

    total = len(df)

    likely = (
        df["prediction"] == "Likely to churn"
    ).sum()

    unlikely = (
        df["prediction"] == "Unlikely to churn"
    ).sum()

    print("Likely to churn:", likely)
    print("Unlikely to churn:", unlikely)

    print(
        "Predicted churn percentage:",
        round((likely / total) * 100, 2),
        "%"
    )

    print()


def print_top_risk_customers(df):

    print("=" * 60)
    print("TOP 10 HIGHEST-RISK CUSTOMERS")
    print("=" * 60)

    top10 = df.sort_values(
        by="risk_score",
        ascending=False
    ).head(10)

    print(
        top10[
            [
                "customer_id",
                "risk_score",
                "prediction",
                "confidence"
            ]
        ].to_string(index=False)
    )

    print()


def main():

    print("ML5 - BATCH SCORING JOB")
    print("=" * 60)
    print()

    customers = load_customers()

    risk_table = build_risk_table(
        customers
    )

    save_risk_table(
        risk_table
    )

    print_summary(
        risk_table
    )

    print_top_risk_customers(
        risk_table
    )

    print("ML5 COMPLETE")


if __name__ == "__main__":
    main()