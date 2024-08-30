import re
import requests as rq
from bs4 import BeautifulSoup
import pandas as pd
import time
import feedparser
from urllib.parse import quote
import csv
import json

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer,PatternAnalyzer
import pandas as pd


def get_news(url):
    data = rq.get(url)
    s = BeautifulSoup(data.text, "html.parser")
    s.prettify()
    if s.find("h1"):
      head_lines = s.find("h1").text
      content = " ".join([para.text for para in s.find_all("p")[1:]])
      return content
    return None

def data_frame_creation(data_frame, all_articles, category):
    for article in all_articles:
        link = article.find("a").get("href")
        news_link = link
        if "https" not in news_link:
            news_link = "https://www.indiatoday.in" + news_link
        content = get_news(news_link)
        if content:
            data_frame["content"].append(content)
            data_frame["link"].append(news_link)
            data_frame["headlines"].append(article.text)
            data_frame["category"].append(category)

def get_titles(search_term, category):
    encoded_search_term = quote(search_term)
    url = f'https://news.google.com/rss/search?q={encoded_search_term}&hl=en-IN&gl=IN&ceid=IN:en'
    feed = feedparser.parse(url)
    stories = []
    for entry in feed.entries:
        story = {
            'headlines': entry.title,
            'link': entry.link,
            'content': "news",
            'category': category
        }
        stories.append(story)
    return stories




def update_json_from_dict(data_frame, json_file):
    """
    Updates the JSON file with data from the provided dictionary, organized by category.
    
    :param data_frame: DataFrame with columns: headlines, link, content, category, sentiment
    :param json_file: Path to the JSON file to update
    """
    organized_data = {}

    for _, row in data_frame.iterrows():
        category = row['category'].lower()
        headline = row['headlines']
        link = row['link']
        sentiment = row['sentiment'].lower()

        if category not in organized_data:
            organized_data[category] = []

        organized_data[category].append({
            "sentiment": sentiment,
            "url": link,
            "headline": headline
        })

    # Write updated data back to the JSON file
    try:
        with open(json_file, 'w') as jsonfile:
            json.dump(organized_data, jsonfile, indent=2)
        print(f"JSON file {json_file} updated successfully.")
    except Exception as e:
        print(f"Error writing JSON file: {e}")

        
if __name__ == "__main__":
    start = time.time()

    # India Today scraping
    urls = ["https://www.indiatoday.in/business", "https://www.indiatoday.in/entertainment", 
            "https://www.indiatoday.in/", "https://www.indiatoday.in/sports", 
            "https://www.indiatoday.in/education"]
    # urls = []
    data_frame = {"headlines": [], "link": [], "content": [], "category": []}

    for url in urls:
        data = rq.get(url)
        if data.status_code == 200:
            print(url, "executed")
            s = BeautifulSoup(data.text, "html.parser")
            all_articles = s.find_all("div", {"class": "B1S3_content__wrap__9mSB6"})
            category = url.split("/")[-1] if url.split("/")[-1] else "General News"
            data_frame_creation(data_frame, all_articles, category)

    df = pd.DataFrame(data_frame)
    df["source"] = "India Today"

    print("India Today scraping time:", time.time() - start)

    # # Google News scraping
    # categories = {
    #     'General News': 'latest news',
    #     'Education': 'education news',
    #     'Entertainment': 'entertainment news',
    #     'Sports': 'sports news',
    #     'Business': 'business news'
    # }

    # all_stories = []
    # for category, search_term in categories.items():
    #     stories = get_titles(search_term, category)
    #     all_stories.extend(stories)

    # df2 = pd.DataFrame(all_stories)
    # df2["source"] = "Google news"

    # # Combine both dataframes
    # final_df = pd.concat([df, df2], ignore_index=True)

    print("Total execution time:", time.time() - start)

    # Save the final dataframe to CSV
    # final_df.to_csv("news_data.csv", index=False)
    # Step 1: Load the dataset
    # data = pd.read_csv('updated_news.csv')
    data = df
    # Step 2: Combine headlines and content into one column
    data['text'] = data["headlines"] + " " + data["content"]

    # Step 3: Define a function to apply TextBlob sentiment analysis
    def get_sentiment(text):
        blob = TextBlob(text, analyzer=PatternAnalyzer())
        sentiment = blob.sentiment
        val = sentiment.polarity
        if val > 0:
            return "Positive"
        return "Negative"

    # Step 4: Apply sentiment analysis to the text column
    data[['sentiment']] = data['text'].apply(lambda x: pd.Series(get_sentiment(x)))


    # print("Data saved to news_data.csv")
    print(data.info())
    json_file = 'news_data.json'  # JSON file to be updated
    update_json_from_dict(data, json_file)
