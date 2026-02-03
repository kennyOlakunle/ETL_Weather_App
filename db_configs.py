from dotenv import load_dotenv
import os

load_dotenv()
conn_string = os.getenv("DATABASE_URL")

def get_db_connection_string():
    return conn_string  
# Example usage
if __name__ == "__main__":
    print("Database Connection String:", get_db_connection_string())    
