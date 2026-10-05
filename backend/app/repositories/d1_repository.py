from app.services.d1_client import d1
import uuid
from datetime import datetime

class D1Repository:
    # --- Employees ---
    async def getEmployees(self):
        return await d1.execute("SELECT * FROM employees ORDER BY created_at DESC")
        
    async def getEmployeeById(self, employee_id: str):
        res = await d1.execute("SELECT * FROM employees WHERE employee_id = ?", [employee_id])
        return res[0] if res else None

    async def getEmployeeByRFID(self, rfid_uid: str):
        res = await d1.execute("SELECT * FROM employees WHERE rfid_uid = ?", [rfid_uid])
        return res[0] if res else None
        
    async def createEmployee(self, data: dict):
        sql = """
        INSERT INTO employees (employee_id, employee_name, rfid_uid, department, workstation, shift, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING *
        """
        res = await d1.execute(sql, [
            data['employee_id'], data['employee_name'], data.get('rfid_uid'), 
            data['department'], data.get('workstation'), data.get('shift'), data.get('status', 'ACTIVE')
        ])
        return res[0] if res else None

    # --- Devices ---
    async def getDevices(self):
        return await d1.execute("SELECT * FROM devices ORDER BY created_at DESC")

    async def getDeviceById(self, device_id: str):
        res = await d1.execute("SELECT * FROM devices WHERE device_id = ?", [device_id])
        return res[0] if res else None
        
    async def createDevice(self, data: dict):
        sql = """
        INSERT INTO devices (device_id, device_name, device_type, workstation, location, status)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING *
        """
        res = await d1.execute(sql, [
            data['device_id'], data.get('device_name'), data.get('device_type', 'WELLBEING_STATION'),
            data.get('workstation'), data.get('location'), data.get('status', 'OFFLINE')
        ])
        return res[0] if res else None

    # --- Feedback Events ---
    async def createFeedbackEvent(self, data: dict):
        event_id = data.get('event_id') or str(uuid.uuid4())
        sql = """
        INSERT INTO feedback_events (event_id, employee_id, device_id, feedback, timestamp)
        VALUES (?, ?, ?, ?, ?)
        RETURNING *
        """
        res = await d1.execute(sql, [
            event_id, data['employee_id'], data.get('device_id'), data['feedback'], data['timestamp']
        ])
        return res[0] if res else None

    async def getFeedbackEvents(self):
        return await d1.execute("SELECT * FROM feedback_events ORDER BY timestamp DESC")

    async def getEmployeeFeedbackHistory(self, employee_id: str):
        return await d1.execute("SELECT * FROM feedback_events WHERE employee_id = ? ORDER BY timestamp DESC", [employee_id])

    # --- Sensors ---
    async def createSensorReading(self, data: dict):
        sql = """
        INSERT INTO sensor_readings (event_id, employee_id, device_id, skin_temperature, heart_rate, spo2, gsr, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING *
        """
        res = await d1.execute(sql, [
            data.get('event_id'), data['employee_id'], data.get('device_id'),
            data.get('skin_temperature'), data.get('heart_rate'), data.get('spo2'), data.get('gsr'), data['timestamp']
        ])
        return res[0] if res else None

    async def getSensorReadings(self):
        return await d1.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC")

    # --- Predictions ---
    async def createPrediction(self, data: dict):
        sql = """
        INSERT INTO ml_predictions (event_id, employee_id, model_name, risk_score, risk_level, prediction, confidence, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING *
        """
        res = await d1.execute(sql, [
            data.get('event_id'), data['employee_id'], data['model_name'], data.get('risk_score'),
            data.get('risk_level'), data.get('prediction'), data.get('confidence'), data.get('explanation')
        ])
        return res[0] if res else None

    async def getPredictions(self):
        return await d1.execute("SELECT * FROM ml_predictions ORDER BY created_at DESC")

    # --- Missing Feedback ---
    async def getMissingFeedbackEvents(self):
        return await d1.execute("SELECT * FROM missing_feedback_events ORDER BY expected_at DESC")

    # --- Dashboard Summary ---
    async def getDashboardSummary(self):
        happy = await d1.execute("SELECT COUNT(*) as count FROM feedback_events WHERE feedback = 'HAPPY'")
        ok = await d1.execute("SELECT COUNT(*) as count FROM feedback_events WHERE feedback = 'OK'")
        sad = await d1.execute("SELECT COUNT(*) as count FROM feedback_events WHERE feedback = 'SAD'")
        total_employees = await d1.execute("SELECT COUNT(*) as count FROM employees WHERE status = 'ACTIVE'")
        
        return {
            "happy_count": happy[0]['count'] if happy else 0,
            "ok_count": ok[0]['count'] if ok else 0,
            "sad_count": sad[0]['count'] if sad else 0,
            "active_employees": total_employees[0]['count'] if total_employees else 0
        }

d1_repo = D1Repository()
