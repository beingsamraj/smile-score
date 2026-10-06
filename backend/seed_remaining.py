import random
from datetime import datetime, timedelta

def main():
    sql_statements = []

    # 1. Generate Devices
    workstations = [f"WS-{i:02d}" for i in range(1, 11)]
    departments = ["Production", "Assembly", "Quality", "Packaging", "Maintenance", "Stores", "Cutting", "Finishing"]
    
    device_ids = []
    
    for i, ws in enumerate(workstations):
        device_id = f"ESP32-{i+1:03d}"
        device_ids.append(device_id)
        sql_statements.append(
            f"INSERT OR IGNORE INTO devices (device_id, device_name, device_type, workstation, location, status) "
            f"VALUES ('{device_id}', 'Wellbeing Station {i+1:02d}', 'WELLBEING_STATION', '{ws}', 'Factory-01', 'ONLINE');"
        )
        
    # 2. Generate Missing Feedback Events
    # We will pick 50 random employees from the 1000 generated
    # and create some missing feedback events
    random.seed(42)
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=4)
    
    for _ in range(50):
        emp_id = f"EMP{random.randint(1, 1000):04d}"
        dev_id = random.choice(device_ids)
        day_offset = random.randint(0, 4)
        expected_time = start_date + timedelta(days=day_offset, hours=14, minutes=30)
        
        status = random.choice(["MISSING", "DETECTED", "REVIEWED"])
        gap_minutes = random.randint(15, 120) if status != "MISSING" else "NULL"
        detected_at = f"'{expected_time + timedelta(minutes=gap_minutes)}'" if gap_minutes != "NULL" else "NULL"
        
        sql_statements.append(
            f"INSERT INTO missing_feedback_events (employee_id, device_id, expected_at, detected_at, gap_minutes, status) "
            f"VALUES ('{emp_id}', '{dev_id}', '{expected_time.isoformat()}Z', {detected_at}, {gap_minutes}, '{status}');"
        )

    output_file = "migrations/0003_seed_remaining_tables.sql"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))
        
    print(f"Generated {len(sql_statements)} statements to {output_file}")

if __name__ == "__main__":
    main()
