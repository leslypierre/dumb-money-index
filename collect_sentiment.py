from datetime import datetime, timezone
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os

PAIRS = [
    "AUDCAD", "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD",
    "CADCHF", "CADJPY", "CHFJPY",
    "EURAUD", "EURCAD", "EURCHF", "EURGBP", "EURJPY", "EURNZD", "EURUSD",
    "GBPAUD", "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD", "GBPUSD",
    "NZDCAD", "NZDCHF", "NZDJPY", "NZDUSD",
    "USDCAD", "USDCHF", "USDJPY"
]

def parse_lots(value):
    return float(value.replace("lots", "").replace(",", "").strip())

def parse_pct(value):
    return float(value.replace("%", "").strip())

def parse_int(value):
    return int(value.replace(",", "").strip())

def get_sentiment_data(pair):
    url = f"https://www.myfxbook.com/community/outlook/{pair}"
    print(f"🔄 Récupération {pair}...")

    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(8)

    try:
        table = driver.find_element(By.ID, "currentMetricsTable")
        rows = table.find_elements(By.TAG_NAME, "tr")
        data_rows = [r.find_elements(By.TAG_NAME, "td") for r in rows]
        parsed_rows = [[cell.text for cell in row] for row in data_rows if row]

        print(f"   ▶️ {pair} : {len(parsed_rows)} lignes trouvées")
        for i, row in enumerate(parsed_rows):
            print(f"      Ligne {i} : {row}")

        short_row = next((r for r in parsed_rows if "Short" in r[0]), None)
        long_row = next((r for r in parsed_rows if "Long" in r[0]), None)

        if not short_row or not long_row:
            raise ValueError("Données Short/Long non trouvées")

        short_pct = parse_pct(short_row[1])
        short_lots = parse_lots(short_row[2])
        short_pos = parse_int(short_row[3])

        long_pct = parse_pct(long_row[1])
        long_lots = parse_lots(long_row[2])
        long_pos = parse_int(long_row[3])

        timestamp = datetime.now(timezone.utc)

        df = pd.DataFrame([{
            "timestamp": timestamp,
            "pair": pair,
            "short_pct": short_pct,
            "short_lots": short_lots,
            "short_pos": short_pos,
            "long_pct": long_pct,
            "long_lots": long_lots,
            "long_pos": long_pos
        }])

        return df

    except Exception as e:
        print(f"❌ Erreur {pair} : {e}")
        return None

    finally:
        driver.quit()

output_dir = "data_sentiment"
os.makedirs(output_dir, exist_ok=True)

for pair in PAIRS:
    df_new = get_sentiment_data(pair)
    if df_new is not None:
        csv_path = os.path.join(output_dir, f"{pair}_sentiment.csv")
        if os.path.exists(csv_path):
            df_existing = pd.read_csv(csv_path)
            df_existing["timestamp"] = pd.to_datetime(df_existing["timestamp"])
            df_all = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_all = df_new

        df_all.to_csv(csv_path, index=False)
        print(f"✅ Enregistré : {csv_path}")

print("\n🎉 Fini ! Toutes les paires ont été mises à jour.")
