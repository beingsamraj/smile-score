from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.repositories.d1_repository import d1_repo
from app.services.d1_client import d1

router = APIRouter(prefix="/api", tags=["D1 Integration"])

# --- Schemas ---
class EmployeeCreate(BaseModel):
    employee_id: str
    employee_name: str
    rfid_uid: Optional[str] = None
    department: str
    workstation: Optional[str] = None
    shift: Optional[str] = None
    status: Optional[str] = 'ACTIVE'

class DeviceCreate(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    device_type: Optional[str] = 'WELLBEING_STATION'
    workstation: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = 'OFFLINE'

class FeedbackCreate(BaseModel):
    # Depending on hardware, they might send rfid_uid or employee_id
    rfid_uid: Optional[str] = None
    employee_id: Optional[str] = None
    device_id: Optional[str] = None
    feedback: str
    timestamp: Optional[str] = None

class SensorCreate(BaseModel):
    event_id: Optional[str] = None
    employee_id: str
    device_id: Optional[str] = None
    skin_temperature: Optional[float] = None
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    gsr: Optional[float] = None
    timestamp: Optional[str] = None

class PredictionCreate(BaseModel):
    event_id: Optional[str] = None
    employee_id: str
    model_name: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    explanation: Optional[str] = None

# --- Employees ---
@router.get("/employees")
async def get_employees():
    return await d1_repo.getEmployees()

@router.get("/employees/{employee_id}")
async def get_employee(employee_id: str):
    emp = await d1_repo.getEmployeeById(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.post("/employees")
async def create_employee(emp: EmployeeCreate):
    res = await d1_repo.createEmployee(emp.dict())
    if not res:
        raise HTTPException(status_code=500, detail="Failed to create employee")
    return res

# --- Devices ---
@router.get("/devices")
async def get_devices():
    return await d1_repo.getDevices()

@router.post("/devices")
async def create_device(dev: DeviceCreate):
    res = await d1_repo.createDevice(dev.dict())
    if not res:
        raise HTTPException(status_code=500, detail="Failed to create device")
    return res

# --- Feedback (Overrides main.py implementation if included after) ---
@router.get("/feedback")
async def get_feedback():
    return await d1_repo.getFeedbackEvents()

@router.post("/feedback")
async def create_feedback(fb: FeedbackCreate):
    feedback_val = fb.feedback.strip().upper()
    if feedback_val not in ["HAPPY", "OK", "SAD"]:
        raise HTTPException(status_code=400, detail="Invalid feedback. Must be HAPPY, OK, or SAD.")
        
    if not fb.rfid_uid and not fb.employee_id:
        raise HTTPException(status_code=400, detail="Either rfid_uid or employee_id must be provided.")
        
    # Identity Verification
    employee = None
    if fb.rfid_uid:
        employee = await d1_repo.getEmployeeByRFID(fb.rfid_uid.strip().upper())
    elif fb.employee_id:
        employee = await d1_repo.getEmployeeById(fb.employee_id)
        
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found or RFID not registered")
        
    if employee.get("status") != "ACTIVE":
        raise HTTPException(status_code=403, detail="Employee is inactive")
        
    timestamp = fb.timestamp or datetime.utcnow().isoformat() + "Z"
    
    data = {
        "event_id": str(uuid.uuid4()),
        "employee_id": employee["employee_id"],
        "device_id": fb.device_id,
        "feedback": feedback_val,
        "timestamp": timestamp
    }
    
    res = await d1_repo.createFeedbackEvent(data)
    if not res:
        raise HTTPException(status_code=500, detail="Failed to record feedback")
        
    return {
        "success": True,
        "message": "Feedback recorded successfully",
        "data": res
    }

# --- Sensors ---
@router.get("/sensors")
async def get_sensors():
    return await d1_repo.getSensorReadings()

@router.post("/sensors")
async def create_sensor(sensor: SensorCreate):
    data = sensor.dict()
    if not data.get('timestamp'):
        data['timestamp'] = datetime.utcnow().isoformat() + "Z"
    res = await d1_repo.createSensorReading(data)
    return res

# --- Predictions ---
@router.get("/predictions")
async def get_predictions():
    return await d1_repo.getPredictions()

@router.post("/predictions")
async def create_prediction(pred: PredictionCreate):
    return await d1_repo.createPrediction(pred.dict())

# --- Missing Feedback ---
@router.get("/missing-feedback")
async def get_missing_feedback():
    return await d1_repo.getMissingFeedbackEvents()

# --- Analytics / Dashboard ---
@router.get("/dashboard")
async def get_dashboard():
    return await d1_repo.getDashboardSummary()
