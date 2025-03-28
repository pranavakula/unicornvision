# Databricks notebook source
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Simple Portfolio").getOrCreate()

# Load main startup dataset
df = spark.read.table("unicornvision.default.main_data")

# Clean column names
df = df.withColumnRenamed("Startup Name", "Startup_Name") \
       .withColumnRenamed("Industry Vertical", "Industry_Vertical") \
       .withColumnRenamed("City  Location", "City_Location") \
       .withColumnRenamed("Investors Name", "Investors_Name") \
       .withColumnRenamed("InvestmentnType", "Investment_Type") \
       .withColumnRenamed("Amount in USD", "Amount_in_USD") \
       .withColumnRenamed("Date dd/mm/yyyy", "Date")

df.show(5)


# COMMAND ----------

startup_names = df.select("Startup_Name").distinct().limit(50).toPandas()["Startup_Name"].tolist()

print("Available Startups:")
for i, s in enumerate(startup_names):
    print(f"{i+1}. {s}")

selected_index = int(input("Select a startup by number: ")) - 1
selected_startup = startup_names[selected_index]
print(f"✅ Selected Startup: {selected_startup}")


# COMMAND ----------

amount_invested = float(input("Enter amount invested (USD): "))
confidence_score = int(input("Enter confidence score (0-100): "))
sentiment_label = input("Enter sentiment (Positive / Neutral / Negative): ")


# COMMAND ----------

roi_base = {"Positive": 0.3, "Neutral": 0.15, "Negative": 0.05}
expected_roi_pct = roi_base.get(sentiment_label, 0.1) + (confidence_score / 1000)

expected_return = round(amount_invested * expected_roi_pct, 2)
projected_value = round(amount_invested + expected_return, 2)


# COMMAND ----------

startup_row = df.filter(df.Startup_Name == selected_startup).limit(1).toPandas().iloc[0]
industry = startup_row["Industry_Vertical"]

portfolio_entry = {
    "Startup": selected_startup,
    "Industry": industry,
    "Amount Invested": amount_invested,
    "Confidence Score": confidence_score,
    "Sentiment": sentiment_label,
    "Expected ROI (%)": round(expected_roi_pct * 100, 2),
    "Expected Return": expected_return,
    "Projected Value": projected_value
}

# Store in list
try:
    portfolio.append(portfolio_entry)
except NameError:
    portfolio = [portfolio_entry]


# COMMAND ----------

import pandas as pd

portfolio_df = pd.DataFrame(portfolio)
display(portfolio_df)

print(f"\n💼 Portfolio Summary")
print(f"💰 Total Invested: ${portfolio_df['Amount Invested'].sum():,.2f}")
print(f"📈 Total Expected Return: ${portfolio_df['Expected Return'].sum():,.2f}")
print(f"📊 Total Projected Value: ${portfolio_df['Projected Value'].sum():,.2f}")


# COMMAND ----------

