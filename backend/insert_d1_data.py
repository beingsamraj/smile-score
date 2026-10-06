import csv
import asyncio
import os
import sys

# Append current dir so we can import d1_client
sys.path.append(os.getcwd())
from app.services.d1_client import d1

CSV_FILE = "worker_1000_5day_afternoon_dataset.csv"
SQL_OUTPUT_FILE = "migrations/0002_seed_data.sql"

def escape_sql(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    # Escape single quotes
    clean_val = str(val).replace("'", "''")
    return f"'{clean_val}'"

async def main():
    print(f"Reading {CSV_FILE}...")
    employees = {}
    feedbacks = []
    sensors = []
    predictions = []

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            emp_id = row["employee_id"]
            
            # 1. Employees (only save once per employee)
            if emp_id not in employees:
                employees[emp_id] = {
                    "employee_id": emp_id,
                    "employee_name": row["employee_name"],
                    "rfid_uid": row["rfid_uid"],
                    "department": row["department"],
                    "workstation": row["workstation"],
                    "shift": row["shift"]
                }
                
            # 2. Feedback Events
            event_id = row["event_id"]
            feedbacks.append({
                "event_id": event_id,
                "employee_id": emp_id,
                "feedback": row["feedback"],
                "timestamp": row["timestamp"]
            })
            
            # 3. Sensor Readings
            sensors.append({
                "event_id": event_id,
                "employee_id": emp_id,
                "skin_temperature": row["skin_temperature"],
                "heart_rate": row["heart_rate"],
                "spo2": row["spo2"],
                "gsr": row["gsr"],
                "timestamp": row["timestamp"]
            })
            
            # 4. ML Predictions
            predictions.append({
                "event_id": event_id,
                "employee_id": emp_id,
                "model_name": "Synthetic Random Forest",
                "risk_score": row["risk_score"],
                "risk_level": row["risk_level"]
            })

    print("Generating SQL seed file...")
    sql_statements = []
    
    # Generate Employee Inserts
    for emp in employees.values():
        sql_statements.append(
            f"INSERT OR IGNORE INTO employees (employee_id, employee_name, rfid_uid, department, workstation, shift) "
            f"VALUES ({escape_sql(emp['employee_id'])}, {escape_sql(emp['employee_name'])}, {escape_sql(emp['rfid_uid'])}, "
            f"{escape_sql(emp['department'])}, {escape_sql(emp['workstation'])}, {escape_sql(emp['shift'])});"
        )

    # Generate Feedback Inserts
    for fb in feedbacks:
        sql_statements.append(
            f"INSERT OR IGNORE INTO feedback_events (event_id, employee_id, feedback, timestamp) "
            f"VALUES ({escape_sql(fb['event_id'])}, {escape_sql(fb['employee_id'])}, {escape_sql(fb['feedback'])}, "
            f"{escape_sql(fb['timestamp'])});"
        )

    # Generate Sensor Inserts
    for sens in sensors:
        sql_statements.append(
            f"INSERT INTO sensor_readings (event_id, employee_id, skin_temperature, heart_rate, spo2, gsr, timestamp) "
            f"VALUES ({escape_sql(sens['event_id'])}, {escape_sql(sens['employee_id'])}, {escape_sql(sens['skin_temperature'])}, "
            f"{escape_sql(sens['heart_rate'])}, {escape_sql(sens['spo2'])}, {escape_sql(sens['gsr'])}, {escape_sql(sens['timestamp'])});"
        )

    # Generate Prediction Inserts
    for pred in predictions:
        sql_statements.append(
            f"INSERT INTO ml_predictions (event_id, employee_id, model_name, risk_score, risk_level) "
            f"VALUES ({escape_sql(pred['event_id'])}, {escape_sql(pred['employee_id'])}, {escape_sql(pred['model_name'])}, "
            f"{escape_sql(pred['risk_score'])}, {escape_sql(pred['risk_level'])});"
        )

    with open(SQL_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))
        
    print(f"Successfully wrote {len(sql_statements)} statements to {SQL_OUTPUT_FILE}.")
    print("Attempting to execute directly via Cloudflare API (this may fail if token is invalid or payload is too large)...")
    
    # We will try inserting just the first 5 employees to test if the API token works
    test_queries = sql_statements[:5]
    try:
        for q in test_queries:
            await d1.execute(q)
        print("API Token is VALID and working! However, sending 16,000 queries over HTTP is slow.")
        print("Please use Wrangler to upload the massive seed file instead.")
    except Exception as e:
        print(f"API Execution Failed: {e}")
        print("\nBecause the API token failed (or payload too big), you must execute it via Wrangler CLI:")
        print(f"npx wrangler d1 execute smile_score --local --file={SQL_OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
