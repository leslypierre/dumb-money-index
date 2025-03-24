# collect_sentiment.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# === CONFIG ===
MAJORS = ["EUR", "GBP", "USD", "AUD", "NZD", "CAD", "CHF", "JPY"]
ALLOWED_PAIRS = [a + b for a in MAJORS for b in MAJORS if a != b]
DATA_DIR = "data"

# === Scraper Myfxbook ===
def get_sentiment_from_myfxbook():
    url = "https://www.myfxbook.com/community/outlook"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table", {"id": "outlookSymbolsTable"})
    rows = table.find("tbody").find_all("tr")

    data = []

    for row in rows:
        try:
            cols = row.find_all("td")
            if not cols or len(cols) < 2:
                continue

            pair = cols[0].text.strip().replace("/", "")
            if pair not in ALLOWED_PAIRS:
                continue

            short_div = row.find("div", class_="progress-bar-danger")
            long_div = row.find("div", class_="progress-bar-success")

            short_pct = float(short_div["style"].split("width:")[1].replace("%;", "").strip())
            long_pct = float(long_div["style"].split("width:")[1].replace("%;", "").strip())

            data.append({
                "pair": pair,
                "long_pct": long_pct,
                "short_pct": short_pct
            })
        except:
            continue

    return data

# === Enregistre dans un CSV par paire ===
def save_data_to_csv(data):
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    now_str = now.strftime("%Y-%m-%d %H:%M")

    os.makedirs(DATA_DIR, exist_ok=True)

    for item in data:
        pair = item["pair"]
        file_path = os.path.join(DATA_DIR, f"{pair}_sentiment.csv")

        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["timestamp", "pair", "long_pct", "short_pct"])

        # Vérifie s’il y a déjà une ligne pour cette heure
        if not ((df["timestamp"] == now_str) & (df["pair"] == pair)).any():
            new_row = pd.DataFrame([{
                "timestamp": now_str,
                "pair": pair,
                "long_pct": item["long_pct"],
                "short_pct": item["short_pct"]
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(file_path, index=False)

if __name__ == "__main__":
    print("⏳ Scraping MyFXBook...")
    sentiment_data = get_sentiment_from_myfxbook()
    save_data_to_csv(sentiment_data)
    print("✅ Données mises à jour.")
