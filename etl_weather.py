import requests
import pandas as pd
from dotenv import load_dotenv
import os
import psycopg2
from datetime import datetime, timezone
import schedule
import time
import logging



load_dotenv()

# Secrets
API_KEY = os.getenv("OPENWEATHER_API_KEY")
DB_URL = os.getenv("DATABASE_URL")

CITY = "Bournemouth,GB"



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("etl_weather.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)



def extract_weather():
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": CITY,
        "appid": API_KEY,
        "units": "metric"  # Gives temp in Celsius
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        utc_now = datetime.now(timezone.utc)
        date_str = utc_now.isoformat().replace("+00:00", "Z")  # Clean UTC with Z

        weather_record = {
            "date": date_str,
            "city": data["name"],
            "temp_kelvin": data["main"]["temp"] + 273.15,  # Convert to Kelvin anyway
            "temp_celsius": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }

        df = pd.DataFrame([weather_record])
        print("Extracted raw data:\n", df)
        return df

    except Exception as e:
        print(f"Extraction failed: {e}")
        return None


def transform_weather(df):
    if df is None or df.empty:
        return None

    # Basic cleaning & enrichment (you can expand this later)
    df = df.copy()  # Avoid SettingWithCopyWarning

    # Round temperatures to 2 decimals
    df["temp_celsius"] = df["temp_celsius"].round(2)
    df["temp_kelvin"] = df["temp_kelvin"].round(2)

    # Capitalize city name (optional)
    df["city"] = df["city"].str.title()

    # Add a simple quality flag (example transformation)
    df["data_quality"] = df["humidity"].apply(lambda h: "Good" if 30 <= h <= 90 else "Check")

    print("\nTransformed data:\n", df)
    return df


def load_to_supabase(df):
    if df is None or df.empty:
        print("No data to load.")
        return

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Insert each row (for small data; later you can use COPY for bulk)
        insert_query = """
        INSERT INTO weather_data (date, city, temp_kelvin, temp_celsius, humidity, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Optional: skip duplicates if you run multiple times
        """

        for _, row in df.iterrows():
            cur.execute(insert_query, (
                row["date"],
                row["city"],
                row["temp_kelvin"],
                row["temp_celsius"],
                row["humidity"],
                row["description"]
            ))

        conn.commit()
        print(f"\nSuccessfully loaded {len(df)} record(s) to Supabase!")

    except Exception as e:
        print(f"Load failed: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()


# Main execution
if __name__ == "__main__":
    print("Starting ETL pipeline for weather data...")
    raw_df = extract_weather()

    if raw_df is not None:
        transformed_df = transform_weather(raw_df)
        if transformed_df is not None:
            load_to_supabase(transformed_df)
    print("ETL pipeline completed!")


    # Add scheduling to run the ETL pipeline every hour


def run_full_etl():
    print(f"\n[{datetime.now(timezone.utc).isoformat()}] Starting scheduled ETL run...")
    raw_df = extract_weather()
    if raw_df is not None:
        transformed_df = transform_weather(raw_df)
        if transformed_df is not None:
            load_to_supabase(transformed_df)
    print("Scheduled run completed!\n")

# Schedule daily at 8:00 AM UTC (adjust time as needed)
schedule.every().day.at("08:00").do(run_full_etl)

# For testing: run every 5 minutes
# schedule.every(1).minutes.do(run_full_etl)

print("Scheduler started. Waiting for next run... (Press Ctrl+C to stop)")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute