import os

os.environ["PYSPARK_PYTHON"] = r"C:\Users\vimalraj.ck\AppData\Local\Programs\Python\Python312\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\vimalraj.ck\AppData\Local\Programs\Python\Python312\python.exe"

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)
from pyspark.sql import functions as F


spark = (
    SparkSession.builder
    .appName("CustomerChurnDE5")
    .master("local[2]")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)


schema = StructType([
    StructField("customerID", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("SeniorCitizen", IntegerType(), True),
    StructField("Partner", StringType(), True),
    StructField("Dependents", StringType(), True),
    StructField("tenure", IntegerType(), True),
    StructField("PhoneService", StringType(), True),
    StructField("MultipleLines", StringType(), True),
    StructField("InternetService", StringType(), True),
    StructField("OnlineSecurity", StringType(), True),
    StructField("OnlineBackup", StringType(), True),
    StructField("DeviceProtection", StringType(), True),
    StructField("TechSupport", StringType(), True),
    StructField("StreamingTV", StringType(), True),
    StructField("StreamingMovies", StringType(), True),
    StructField("Contract", StringType(), True),
    StructField("PaperlessBilling", StringType(), True),
    StructField("PaymentMethod", StringType(), True),
    StructField("MonthlyCharges", DoubleType(), True),
    StructField("TotalCharges", StringType(), True),
    StructField("Churn", StringType(), True)
])


df = (
    spark.read
    .option("header", True)
    .schema(schema)
    .csv("customer_churn.csv")
)


print()
print("CUSTOMER DATA SCHEMA")
print("--------------------")

df.printSchema()


print()
print("CUSTOMER COUNT")
print("--------------")

print(df.count())


df = df.withColumn(
    "TotalCharges",
    F.regexp_replace(
        F.col("TotalCharges"),
        r"^\s*$",
        ""
    )
)


df = df.withColumn(
    "TotalCharges",
    F.col("TotalCharges").cast(DoubleType())
)


df = df.withColumn(
    "churn_encoded",
    F.when(
        F.col("Churn") == "Yes",
        1
    ).otherwise(0)
)


print()
print("CONTRACT CHURN SUMMARY")
print("----------------------")

contract_summary = (
    df.groupBy("Contract")
    .agg(
        F.count("*").alias("customer_count"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy(
        F.col("churn_rate").desc()
    )
)

contract_summary.show(
    truncate=False
)


print()
print("INTERNET SERVICE SUMMARY")
print("------------------------")

internet_summary = (
    df.groupBy("InternetService")
    .agg(
        F.avg("MonthlyCharges").alias("avg_monthly_charges"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy(
        F.col("churn_rate").desc()
    )
)

internet_summary.show(
    truncate=False
)


output_path = "data/spark_output/contract_summary"


(
    contract_summary
    .write
    .mode("overwrite")
    .partitionBy("Contract")
    .parquet(output_path)
)


print()
print("PARQUET WRITTEN")
print("---------------")

print(output_path)


parquet_df = spark.read.parquet(
    output_path
)


print()
print("PARQUET SCHEMA")
print("--------------")

parquet_df.printSchema()


print()
print("PARQUET ROW COUNT")
print("-----------------")

print(parquet_df.count())


spark.stop()