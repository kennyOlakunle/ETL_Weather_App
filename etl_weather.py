
import requests
import pandas as pd
from dotenv import load_dotenv
import os
import psycopg2
from datetime import datetime, timezone

# Prefect imports
from prefect import flow, task
from prefect.logging import get_run_logger

# Load environment variables
load_dotenv()

# Secrets from .env
API_KEY = os.getenv("OPENWEATHER_API_KEY")
DB_URL = os.getenv("DATABASE_URL")

# Configuration
CITY = "Bournemouth,GB"  # City,Country code


@task(retries=2, retry_delay_seconds=30)
def extract_weather_task():
    logger = get_run_logger()
    logger.info(f"Extracting current weather for {CITY}")

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": CITY,
        "appid": API_KEY,
        "units": "metric"  # Returns temperature in Celsius
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        utc_now = datetime.now(timezone.utc)
        date_str = utc_now.isoformat().replace("+00:00", "Z")  # ISO with 'Z' for UTC

        weather_record = {
            "date": date_str,
            "city": data["name"],
            "temp_kelvin": round(data["main"]["temp"] + 273.15, 2),
            "temp_celsius": round(data["main"]["temp"], 2),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }

        df = pd.DataFrame([weather_record])
        logger.info("Extraction successful")
        logger.debug(f"Extracted data:\n{df.to_string()}")
        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid response data: {e}")
        raise


@task(retries=1, retry_delay_seconds=10)
def transform_weather_task(raw_df):
    logger = get_run_logger()

    if raw_df is None or raw_df.empty:
        logger.warning("No data received for transformation")
        return None

    df = raw_df.copy()

    # Additional light transformations / quality checks
    df["city"] = df["city"].str.title()
    df["data_quality"] = df["humidity"].apply(
        lambda h: "Good" if 20 <= h <= 100 else "Suspicious"
    )

    logger.info("Transformation complete")
    logger.debug(f"Transformed data:\n{df.to_string()}")
    return df


@task(retries=3, retry_delay_seconds=60)
def load_to_supabase_task(df):
    logger = get_run_logger()

    if df is None or df.empty:
        logger.warning("No data to load into Supabase")
        return

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        insert_query = """
        INSERT INTO weather_data 
            (date, city, temp_kelvin, temp_celsius, humidity, description)
        VALUES 
            (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
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
        logger.info(f"Successfully inserted {len(df)} record(s) into weather_data table")

    except Exception as e:
        logger.error(f"Database load failed: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@flow(name="Daily Bournemouth Weather ETL", log_prints=True)
def daily_weather_etl():
    logger = get_run_logger()
    logger.info("Starting daily weather ETL pipeline")

    raw_data = extract_weather_task()
    transformed_data = transform_weather_task(raw_data)
    load_to_supabase_task(transformed_data)

    logger.info("Pipeline execution completed successfully")


# For local testing / manual runs
if __name__ == "__main__":
    daily_weather_etl()