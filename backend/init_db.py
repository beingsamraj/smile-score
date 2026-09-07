import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL found.")
    exit(1)

print("Connecting to DB...")
try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Executing schema.sql...")
    with open("schema.sql", "r") as f:
        sql = f.read()
        
    cursor.execute(sql)
    print("Schema applied successfully!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
