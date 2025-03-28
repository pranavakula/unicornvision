# Databricks notebook source
# Replace this with your actual News API key
NEWS_API_KEY = "81aa44bb36fd41e2911d4471e36b0042"


# COMMAND ----------

import requests

def fetch_news_articles(startup_name, max_articles=10):
    url = f"https://newsapi.org/v2/everything?q={startup_name}&sortBy=publishedAt&pageSize={max_articles}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        articles = response.json()["articles"]
        return articles
    else:
        print(f"Error: {response.status_code}")
        return []


# COMMAND ----------

from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # Range: -1 to 1
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity


# COMMAND ----------

# MAGIC %pip install textblob
# MAGIC

# COMMAND ----------

def summarize_sentiment(articles):
    sentiment_data = {"Positive": 0, "Negative": 0, "Neutral": 0}
    insights = []

    for article in articles:
        title = article["title"]
        description = article.get("description") or ""
        full_text = f"{title}. {description}"
        sentiment, score = analyze_sentiment(full_text)
        sentiment_data[sentiment] += 1
        insights.append((title, sentiment, round(score, 3)))

    return sentiment_data, insights


# COMMAND ----------

# Example usage:
startup_name = input("Enter startup name for sentiment analysis: ")
articles = fetch_news_articles(startup_name)

if articles:
    sentiment_counts, sentiment_insights = summarize_sentiment(articles)

    print("\n📊 Sentiment Distribution:")
    for sentiment, count in sentiment_counts.items():
        print(f"{sentiment}: {count}")

    print("\n📰 Article Insights:")
    for title, sentiment, score in sentiment_insights:
        print(f"- [{sentiment} | {score}] {title}")
else:
    print("No articles found.")


# COMMAND ----------

