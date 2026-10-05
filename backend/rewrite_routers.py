import os

# 1. WORKERS ROUTER
workers_code = """
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/workers", tags=["Workers"])

@router.get("")
async def get_workers(factory_id: str = None, department_id: str = None, status: str = None):
    res = await d1.execute("SELECT id, employee_id as worker_id, employee_name as name, department as department_name, status FROM employees")
    for r in res:
        r['status'] = True if r['status'] == 'ACTIVE' else False
    return res

@router.get("/{worker_id}")
async def get_worker(worker_id: str):
    return {}
"""

# 2. DEVICES ROUTER
devices_code = """
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("")
async def get_devices(factory_id: str = None, type: str = None, status: str = None):
    res = await d1.execute("SELECT id, device_id as id, device_name as name, device_type as type, status, location as factory_name FROM devices")
    return res

@router.get("/{device_id}")
async def get_device(device_id: str):
    return {}
"""

# 3. FACTORIES ROUTER
factories_code = """
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/factories", tags=["Factories"])

@router.get("")
async def get_factories(status: str = None):
    # Mocking factories since the new D1 schema removed the factories table
    return [{"factory_id": "FAC001", "factory_name": "Main Plant", "status": True}]
"""

# 4. USERS ROUTER
users_code = """
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("")
async def get_users(factory_id: str = None, role: str = None, status: str = None):
    # Mocking users since D1 schema dropped it
    return [{"user_id": "USR001", "name": "Admin", "email": "admin@smilescore.com", "role": "ADMIN", "status": True}]
"""

# 5. REPORTS ROUTER
reports_code = """
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("")
async def get_reports():
    return []
"""

base = "e:/smile-score/backend/app/routers"
with open(f"{base}/workers.py", "w") as f: f.write(workers_code)
with open(f"{base}/devices.py", "w") as f: f.write(devices_code)
with open(f"{base}/factories.py", "w") as f: f.write(factories_code)
with open(f"{base}/users.py", "w") as f: f.write(users_code)
with open(f"{base}/reports.py", "w") as f: f.write(reports_code)

print("Rewrote routers successfully!")
