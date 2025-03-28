# Databricks notebook source
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("Investment Council").getOrCreate()

# ✅ Load dataset correctly from the Delta table
df = spark.read.table("unicornvision.default.main_data")

# Show first 5 rows
df.show(5)


# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("Date", StringType(), True),  # Keep as String if format is inconsistent
    StructField("Startup_Name", StringType(), True),
    StructField("Industry_Vertical", StringType(), True),
    StructField("Sub_Vertical", StringType(), True),
    StructField("City_Location", StringType(), True),
    StructField("Investors_Name", StringType(), True),
    StructField("Investment_Type", StringType(), True),
    StructField("Amount_in_USD", StringType(), True)  # Change to IntegerType() if properly formatted
])

df = spark.read.table("unicornvision.default.main_data")
df.show(5)


# COMMAND ----------

from pyspark.sql.functions import col, regexp_replace, to_date

# Convert Amount in USD to a clean numeric format
df = df.withColumn("Amount_in_USD", regexp_replace(col("Amount in USD"), ",", "").cast("double"))

# Convert Date to proper DateType format
df = df.withColumn("Date dd/mm/yyyy", to_date(col("Date dd/mm/yyyy"), "dd-MM-yyyy"))


# Drop any rows with missing key values
df = df.dropna()

df.show(5)


# COMMAND ----------

# Define the five investment agents and their roles
agents = {
    "Visionary": "Optimistic about the startup's future and long-term growth.",
    "Skeptic": "Identifies risks, weaknesses, and potential failures.",
    "Analyst": "Provides data-driven insights based on past performance and market trends.",
    "Scout": "Compares the startup with competitors in the industry.",
    "Oracle": "Gives a final investment verdict after analyzing all factors."
}

# Print agent roles
for agent, role in agents.items():
    print(f"🔹 {agent}: {role}")


# COMMAND ----------

dbutils.fs.ls("/")
dbutils.fs.ls("dbfs:/")



# COMMAND ----------

dbutils.fs.ls("dbfs:/models/")


# COMMAND ----------

import os
import shutil

# Define paths
dbfs_model_path = "/dbfs/models/mistral-7b/"  # Convert dbfs:/ to /dbfs/
local_model_path = "/tmp/mistral-7b/"

# Ensure the local directory is empty before copying
if os.path.exists(local_model_path):
    shutil.rmtree(local_model_path)

# Copy from DBFS to local directory
shutil.copytree(dbfs_model_path, local_model_path)

print("✅ Model copied from DBFS to local path!")


# COMMAND ----------

from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "/tmp/mistral-7b/"  # Local copy of Mistral
tokenizer = AutoTokenizer.from_pretrained(model_path)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    torch_dtype="auto",                # enables float16 if supported
    offload_folder="/tmp/offload"     # ✅ this is the fix
)

print("✅ Mistral-7B successfully loaded!")


# COMMAND ----------

class InvestmentAgent:
    def __init__(self, name, perspective):
        self.name = name
        self.perspective = perspective

    def analyze(self, startup_details, model, tokenizer):
        prompt = f"""You are {self.name}, an investment expert.
Analyze the startup "{startup_details}" from the perspective of {self.perspective}.
Give an insight and your confidence score out of 100.

Respond in format:
Insight: ...
Confidence Score: ...
"""
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_length=120,          # reduced for speed
                temperature=0.7,
                do_sample=True
            )
        return tokenizer.decode(output[0], skip_special_tokens=True)


# COMMAND ----------

agents = [
    InvestmentAgent("Visionary", "long-term growth and innovation"),
    InvestmentAgent("Skeptic", "risks and market challenges"),
    InvestmentAgent("Analyst", "financial health and past funding"),
    InvestmentAgent("Scout", "competition and market trends"),
    InvestmentAgent("Oracle", "holistic overview and final verdict")
]


# COMMAND ----------

print("📌 Choose how to input startup information:")
print("1️⃣  Select from dropdown list")
print("2️⃣  Manually enter startup details")

choice_mode = input("Enter 1 or 2: ").strip()

if choice_mode == "1":
    startup_names = df.select("Startup Name").distinct().limit(50).toPandas()["Startup Name"].tolist()
    print("\n📋 Available Startups:")
    for i, name in enumerate(startup_names):
        print(f"{i+1}. {name}")
    
    choice = input("\n🔎 Enter the number or name of a startup: ").strip()
    if choice.isdigit():
        selected_startup = startup_names[int(choice)-1]
    else:
        selected_startup = choice

    startup_details = f"Startup Name: {selected_startup}"

elif choice_mode == "2":
    print("\n📝 Enter startup details manually:")
    name = input("Startup Name: ")
    industry = input("Industry Vertical: ")
    location = input("Location (City): ")
    funding = input("Funding Amount in USD: ")
    stage = input("Funding Stage (e.g. Series A): ")

    startup_details = f"""
    Startup Name: {name}
    Industry: {industry}
    Location: {location}
    Funding: ${funding}
    Stage: {stage}
    """.strip()
else:
    print("❌ Invalid choice. Please enter 1 or 2.")
    startup_details = ""


# COMMAND ----------

import torch
torch.cuda.is_available()


# COMMAND ----------

print("🧪 Testing with 1 agent only...")
result = agents[0].analyze(startup_details, model, tokenizer)
print(f"\n🧠 {agents[0].name} Insight:\n{result}")


# COMMAND ----------

test_prompt = """
You are a startup analyst.
Analyze the startup "Zetwerk", and give a short insight and confidence score out of 100.

Respond in format:
Insight: ...
Confidence Score: ...
"""

inputs = tokenizer(test_prompt, return_tensors="pt").to("cuda")

import time
start = time.time()
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=80, temperature=0.7, do_sample=True)

print(tokenizer.decode(output[0], skip_special_tokens=True))
print("⏱️ Total time:", round(time.time() - start, 2), "seconds")


# COMMAND ----------

print(model)


# COMMAND ----------

