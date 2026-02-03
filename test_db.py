import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()  # Load .env
conn_string = os.getenv("DATABASE_URL")

if conn_string is None:
    print("ERROR: DATABASE_URL not found in env! Check .env file and key name.")
else:
    try:
        conn = psycopg2.connect(conn_string)
        print("Connection successful! Using Transaction Pooler (6543).")
        conn.close()
    except Exception as e:
        print("Connection failed:", str(e))