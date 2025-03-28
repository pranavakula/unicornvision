# Databricks notebook source
from pyspark.sql import SparkSession

# Start Spark session
spark = SparkSession.builder.appName("Competitor Analysis").getOrCreate()

# Load the Delta table
df = spark.read.table("unicornvision.default.main_data")

# Display schema and first few rows
df.printSchema()
df.show(5)


# COMMAND ----------

from pyspark.sql.functions import col

# Rename columns to be SQL-friendly (no spaces)
df = df.withColumnRenamed("Date dd/mm/yyyy", "Date") \
       .withColumnRenamed("Startup Name", "Startup_Name") \
       .withColumnRenamed("Industry Vertical", "Industry_Vertical") \
       .withColumnRenamed("City  Location", "City_Location") \
       .withColumnRenamed("Investors Name", "Investors_Name") \
       .withColumnRenamed("InvestmentnType", "Investment_Type") \
       .withColumnRenamed("Amount in USD", "Amount_in_USD")

df.show(5)


# COMMAND ----------

# Collect distinct startup names (limit for dropdown simulation)
startup_list = df.select("Startup_Name").distinct().limit(50).toPandas()["Startup_Name"].tolist()

# Show as dropdown options
print("Available Startups:")
for i, s in enumerate(startup_list):
    print(f"{i+1}. {s}")

# Select 2 startups
s1 = int(input("Select Startup 1 (enter number): ")) - 1
s2 = int(input("Select Startup 2 (enter number): ")) - 1

startup_1 = startup_list[s1]
startup_2 = startup_list[s2]

print(f"\n✅ Selected Startups: {startup_1} vs {startup_2}")


# COMMAND ----------

# Fetch their rows
startup_df_1 = df.filter(col("Startup_Name") == startup_1)
startup_df_2 = df.filter(col("Startup_Name") == startup_2)

# Convert to pandas for easier display
pdf1 = startup_df_1.toPandas()
pdf2 = startup_df_2.toPandas()

# Show comparison
print(f"\n📊 {startup_1} Details:\n", pdf1.head(1).T)
print(f"\n📊 {startup_2} Details:\n", pdf2.head(1).T)


# COMMAND ----------

def compare_startups(pdf1, pdf2):
    s1 = pdf1.iloc[0]
    s2 = pdf2.iloc[0]
    
    print("\n📍 Comparison Summary:")
    print(f"- Industry: {s1['Industry_Vertical']} vs {s2['Industry_Vertical']}")
    print(f"- SubVertical: {s1['SubVertical']} vs {s2['SubVertical']}")
    print(f"- City: {s1['City_Location']} vs {s2['City_Location']}")
    print(f"- Investment Type: {s1['Investment_Type']} vs {s2['Investment_Type']}")
    print(f"- Investors: {s1['Investors_Name']} vs {s2['Investors_Name']}")
    
    try:
        amt1 = float(str(s1['Amount_in_USD']).replace(',', ''))
        amt2 = float(str(s2['Amount_in_USD']).replace(',', ''))
        print(f"- Funding: ${amt1:,.0f} vs ${amt2:,.0f}")
    except:
        print("- Funding: Could not parse one or both amounts.")

compare_startups(pdf1, pdf2)


# COMMAND ----------

