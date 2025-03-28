# Databricks notebook source
import pandas as pd

# Use this exact path style for Pandas (NOT spark.read)
file_path = "/Workspace/Users/am.en.u4cse22328@am.students.amrita.edu/market_main.csv"

# Load the CSV
market_pdf = pd.read_csv(file_path)

# Preview the data
market_pdf.info()
market_pdf.head()


# COMMAND ----------

# Clean funding amount columns using exact names
market_pdf["Total Funding Amount USD"] = pd.to_numeric(
    market_pdf["Total Funding Amount Currency (in USD)"].astype(str).str.replace("[$,]", "", regex=True),
    errors="coerce"
)

market_pdf["Last Funding Amount USD"] = pd.to_numeric(
    market_pdf["Last Funding Amount Currency (in USD)"].astype(str).str.replace("[$,]", "", regex=True),
    errors="coerce"
)


# COMMAND ----------

# Regenerate variables needed for summary
category_funding = (
    market_pdf.groupby("Categories")["Total Funding Amount USD"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

region_funding = (
    market_pdf.groupby("Headquarters Regions")["Total Funding Amount USD"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

top_funded = market_pdf[["Organization Name", "Total Funding Amount USD"]].dropna()
top_funded = top_funded.sort_values(by="Total Funding Amount USD", ascending=False).head(10)

status_counts = market_pdf["Operating Status"].value_counts()
type_funding = market_pdf["Last Funding Type"].value_counts().head(10)

# Generate summary
top_category = category_funding.idxmax()
top_region = region_funding.idxmax()
top_startup = top_funded.iloc[0]["Organization Name"]
most_common_status = status_counts.idxmax()
most_common_funding_type = type_funding.idxmax()

summary = f"""
📊 Market Summary:

- The most funded category is **{top_category}**.
- The region attracting the highest funding is **{top_region}**.
- The top funded startup is **{top_startup}**.
- Most startups are currently **{most_common_status}**.
- The most common type of last funding round is **{most_common_funding_type}**.
"""

print(summary)


# COMMAND ----------

import os

# Ensure folder exists
os.makedirs("/dbfs/FileStore", exist_ok=True)

# Save summary
summary_path = "/dbfs/FileStore/market_summary.txt"

with open(summary_path, "w") as f:
    f.write(summary.strip())

print("✅ Summary saved to:", summary_path)


# COMMAND ----------

import matplotlib.pyplot as plt

# ✅ 1. Top 10 Categories by Total Funding
category_funding = (
    market_pdf.groupby("Categories")["Total Funding Amount USD"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))
category_funding.plot(kind="bar")
plt.title("💰 Top 10 Categories by Total Funding")
plt.ylabel("Total Funding (USD)")
plt.xticks(rotation=45, ha="right")
plt.grid(True)
plt.tight_layout()
plt.show()


# ✅ 2. Operating Status Distribution (Pie Chart)
status_counts = market_pdf["Operating Status"].value_counts()

plt.figure(figsize=(6, 6))
status_counts.plot(kind="pie", autopct="%1.1f%%", startangle=140)
plt.title("📊 Operating Status of Startups")
plt.ylabel("")
plt.tight_layout()
plt.show()


# ✅ 3. Top 10 Regions by Total Funding
region_funding = (
    market_pdf.groupby("Headquarters Regions")["Total Funding Amount USD"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))
region_funding.plot(kind="bar", color="orange")
plt.title("📍 Top 10 Regions by Total Funding")
plt.ylabel("Funding (USD)")
plt.xticks(rotation=45, ha="right")
plt.grid(True)
plt.tight_layout()
plt.show()


# ✅ 4. Top 10 Funded Startups
top_funded = market_pdf[["Organization Name", "Total Funding Amount USD"]].dropna()
top_funded = top_funded.sort_values(by="Total Funding Amount USD", ascending=False).head(10)

plt.figure(figsize=(10, 6))
plt.bar(top_funded["Organization Name"], top_funded["Total Funding Amount USD"])
plt.title("🏆 Top 10 Funded Startups")
plt.xticks(rotation=45, ha="right")
plt.ylabel("Funding (USD)")
plt.tight_layout()
plt.show()


# ✅ 5. Startups Founded Per Year
market_pdf["Founded Date"] = pd.to_datetime(market_pdf["Founded Date"], errors="coerce")
market_pdf["Founded Year"] = market_pdf["Founded Date"].dt.year
startup_years = market_pdf["Founded Year"].value_counts().sort_index()

plt.figure(figsize=(12, 6))
startup_years.plot(kind="line", marker="o")
plt.title("📈 Startups Founded Per Year")
plt.xlabel("Year")
plt.ylabel("Number of Startups")
plt.grid(True)
plt.tight_layout()
plt.show()


# ✅ 6. Total Funding Over Time
funding_by_year = (
    market_pdf.groupby("Founded Year")["Total Funding Amount USD"]
    .sum()
    .dropna()
    .sort_index()
)

plt.figure(figsize=(12, 6))
funding_by_year.plot(kind="line", marker="o", color="green")
plt.title("💸 Total Funding Over Time")
plt.xlabel("Year")
plt.ylabel("Funding (USD)")
plt.grid(True)
plt.tight_layout()
plt.show()


# ✅ 7. Funding Status Distribution (Bar Chart)
status_funding = market_pdf["Funding Status"].value_counts()

plt.figure(figsize=(8, 5))
status_funding.plot(kind="bar")
plt.title("🏷️ Funding Status Distribution")
plt.ylabel("Number of Startups")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ✅ 8. Most Common Last Funding Types
type_funding = market_pdf["Last Funding Type"].value_counts().head(10)

plt.figure(figsize=(10, 6))
type_funding.plot(kind="bar", color="purple")
plt.title("🔖 Most Common Last Funding Types")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# COMMAND ----------

