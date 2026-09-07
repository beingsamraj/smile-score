from fastapi import APIRouter, HTTPException, Query, status, File, UploadFile
from typing import Optional
from app.database import supabase
from app.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse, WorkerListResponse
from app.schemas.import_schemas import CsvValidationPreview, CsvRowError, CsvImportResponse
import uuid
from datetime import datetime, timezone
import csv
import io

router = APIRouter(
    prefix="/api/workers",
    tags=["Workers"]
)

def map_db_worker_to_response(worker_data: dict, factory_name: Optional[str] = None, department_name: Optional[str] = None) -> dict:
    return {
        "worker_id": worker_data.get("worker_id", ""),
        "employee_id": worker_data.get("employee_id", ""),
        "name": worker_data.get("name", ""),
        "factory_id": worker_data.get("factory_id", ""),
        "factory_name": factory_name,
        "department_id": worker_data.get("department_id", ""),
        "department_name": department_name,
        "rfid_uid": worker_data.get("rfid_uid", ""),
        "designation": worker_data.get("designation"),
        "status": worker_data.get("status", True),
        "created_at": worker_data.get("created_at")
    }

@router.get("", response_model=WorkerListResponse)
def get_workers(
    search: Optional[str] = None,
    factory_id: Optional[str] = None,
    department_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        query = supabase.table("workers").select("*")
        
        if factory_id:
            query = query.eq("factory_id", factory_id)
        if department_id:
            query = query.eq("department_id", department_id)
        if status_filter:
            if status_filter.lower() == "active":
                query = query.eq("status", True)
            elif status_filter.lower() == "inactive":
                query = query.eq("status", False)
            
        res = query.execute()
        workers_data = res.data or []
        
        if search:
            search_lower = search.lower()
            workers_data = [
                w for w in workers_data
                if (w.get("name") and search_lower in w["name"].lower()) or
                   (w.get("employee_id") and search_lower in w["employee_id"].lower()) or
                   (w.get("rfid_uid") and search_lower in w["rfid_uid"].lower())
            ]
            
        total = len(workers_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = workers_data[start:end]
        
        # Resolve names
        factory_ids = list(set([w.get("factory_id") for w in paginated_data if w.get("factory_id")]))
        dept_ids = list(set([w.get("department_id") for w in paginated_data if w.get("department_id")]))
        
        factory_map = {}
        if factory_ids:
            fac_res = supabase.table("factories").select("factory_id, factory_name").in_("factory_id", factory_ids).execute()
            for fac in (fac_res.data or []):
                factory_map[fac["factory_id"]] = fac["factory_name"]
                
        dept_map = {}
        if dept_ids:
            dept_res = supabase.table("departments").select("department_id, department_name").in_("department_id", dept_ids).execute()
            for dept in (dept_res.data or []):
                dept_map[dept["department_id"]] = dept["department_name"]
                
        response_data = []
        for w in paginated_data:
            response_data.append(map_db_worker_to_response(
                w, 
                factory_map.get(w.get("factory_id")), 
                dept_map.get(w.get("department_id"))
            ))
            
        return {
            "data": response_data,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: str):
    try:
        res = supabase.table("workers").select("*").eq("worker_id", worker_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Worker not found")
            
        worker_data = res.data[0]
        
        factory_name = None
        if worker_data.get("factory_id"):
            fac_res = supabase.table("factories").select("factory_name").eq("factory_id", worker_data["factory_id"]).execute()
            if fac_res.data:
                factory_name = fac_res.data[0]["factory_name"]
                
        department_name = None
        if worker_data.get("department_id"):
            dept_res = supabase.table("departments").select("department_name").eq("department_id", worker_data["department_id"]).execute()
            if dept_res.data:
                department_name = dept_res.data[0]["department_name"]
                
        return map_db_worker_to_response(worker_data, factory_name, department_name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def create_worker(worker: WorkerCreate):
    try:
        # Check unique RFID
        if worker.rfid_uid:
            res = supabase.table("workers").select("worker_id").eq("rfid_uid", worker.rfid_uid).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="RFID already exists")
                
        new_worker_id = "W" + uuid.uuid4().hex[:5].upper()
        emp_id = "EMP-" + uuid.uuid4().hex[:6].upper()
        
        new_worker = {
            "worker_id": new_worker_id,
            "factory_id": worker.factory_id,
            "department_id": worker.department_id,
            "employee_id": emp_id,
            "name": worker.name,
            "rfid_uid": worker.rfid_uid,
            "designation": worker.designation,
            "status": worker.status,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        supabase.table("workers").insert(new_worker).execute()
        return get_worker(new_worker_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: str, worker: WorkerUpdate):
    try:
        existing = supabase.table("workers").select("*").eq("worker_id", worker_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Worker not found")
            
        if worker.rfid_uid and worker.rfid_uid != existing.data[0].get("rfid_uid"):
            res = supabase.table("workers").select("worker_id").eq("rfid_uid", worker.rfid_uid).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="RFID already exists")
                
        update_data = {}
        if worker.name is not None: update_data["name"] = worker.name
        if worker.factory_id is not None: update_data["factory_id"] = worker.factory_id
        if worker.department_id is not None: update_data["department_id"] = worker.department_id
        if worker.rfid_uid is not None: update_data["rfid_uid"] = worker.rfid_uid
        if worker.designation is not None: update_data["designation"] = worker.designation
        if worker.status is not None: update_data["status"] = worker.status
            
        if update_data:
            supabase.table("workers").update(update_data).eq("worker_id", worker_id).execute()
            
        return get_worker(worker_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worker(worker_id: str):
    try:
        existing = supabase.table("workers").select("*").eq("worker_id", worker_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Worker not found")
            
        update_data = {"status": False}
        supabase.table("workers").update(update_data).eq("worker_id", worker_id).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CSV Bulk Import Logic

def parse_and_validate_workers_csv(file_content: str):
    reader = csv.DictReader(io.StringIO(file_content))
    expected_headers = ['name', 'factory_id', 'department_id', 'rfid_uid', 'designation', 'status']
    
    actual_headers = [h.strip().lower() for h in reader.fieldnames or []]
    missing_headers = [h for h in expected_headers if h not in actual_headers]
    if missing_headers:
        raise ValueError(f"Invalid CSV headers. Missing: {', '.join(missing_headers)}")

    fac_res = supabase.table('factories').select('factory_id').execute()
    existing_factory_ids = {f['factory_id'] for f in fac_res.data or []}
    
    dept_res = supabase.table('departments').select('department_id').execute()
    existing_dept_ids = {d['department_id'] for d in dept_res.data or []}
    
    workers_res = supabase.table('workers').select('rfid_uid').execute()
    existing_rfids = {w['rfid_uid'] for w in workers_res.data or [] if w.get('rfid_uid')}
    
    csv_rfids = set()

    total_rows = 0
    errors = []
    valid_rows = 0
    parsed_data = []

    for idx, row in enumerate(reader, start=2):
        total_rows += 1
        row_errors = []
        
        norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
        
        name = norm_row.get('name')
        factory_id = norm_row.get('factory_id')
        department_id = norm_row.get('department_id')
        rfid_uid = norm_row.get('rfid_uid')
        designation = norm_row.get('designation')
        status = norm_row.get('status', 'active').lower()

        if not name:
            row_errors.append('Name is required.')
            
        if not factory_id or factory_id not in existing_factory_ids:
            row_errors.append(f"Invalid or missing Factory ID: {factory_id}")
            
        if not department_id or department_id not in existing_dept_ids:
            row_errors.append(f"Invalid or missing Department ID: {department_id}")
                
        if rfid_uid:
            rfid_norm = rfid_uid.upper().replace(' ', '')
            if rfid_norm in existing_rfids:
                row_errors.append(f"RFID UID {rfid_norm} is already assigned in database.")
            if rfid_norm in csv_rfids:
                row_errors.append(f"RFID UID {rfid_norm} is duplicated in the uploaded CSV.")
            csv_rfids.add(rfid_norm)
            norm_row['rfid_uid'] = rfid_norm
        else:
            row_errors.append('RFID UID is required.')
            
        if status not in ['active', 'inactive']:
            row_errors.append(f"Invalid status '{status}'. Must be active or inactive.")
            
        if row_errors:
            errors.append(CsvRowError(row=idx, errors=row_errors))
        else:
            valid_rows += 1
            parsed_data.append({
                'name': name,
                'factory_id': factory_id,
                'department_id': department_id,
                'rfid_uid': norm_row.get('rfid_uid'),
                'designation': designation or None,
                'status': True if status == 'active' else False
            })
            
    if total_rows == 0:
        raise ValueError('CSV contains no records.')
        
    return {
        'valid': len(errors) == 0,
        'total_rows': total_rows,
        'valid_rows': valid_rows,
        'invalid_rows': len(errors),
        'errors': errors,
        'parsed_data': parsed_data
    }

@router.post("/import/validate", response_model=CsvValidationPreview)
async def validate_workers_import(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .csv files are supported.")
        
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="CSV file is too large. Maximum allowed size is 5 MB.")
        
    try:
        decoded_content = content.decode('utf-8-sig')
        result = parse_and_validate_workers_csv(decoded_content)
        return CsvValidationPreview(
            valid=result['valid'],
            total_rows=result['total_rows'],
            valid_rows=result['valid_rows'],
            invalid_rows=result['invalid_rows'],
            errors=result['errors']
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse CSV: {str(e)}")

@router.post("/import", response_model=CsvImportResponse)
async def import_workers(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .csv files are supported.")
        
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="CSV file is too large. Maximum allowed size is 5 MB.")
        
    try:
        decoded_content = content.decode('utf-8-sig')
        result = parse_and_validate_workers_csv(decoded_content)
        
        if not result['valid']:
            raise HTTPException(status_code=400, detail="CSV contains validation errors. Please fix them before importing.")
            
        if result['total_rows'] > 5000:
            raise HTTPException(status_code=400, detail="CSV contains too many rows. Maximum allowed rows: 5000.")
            
        parsed_data = result['parsed_data']
        insert_records = []
        
        for row in parsed_data:
            new_worker_id = "W" + uuid.uuid4().hex[:5].upper()
            emp_code = "EMP-" + uuid.uuid4().hex[:6].upper()
            
            insert_records.append({
                "worker_id": new_worker_id,
                "employee_id": emp_code,
                "name": row['name'],
                "factory_id": row['factory_id'],
                "department_id": row['department_id'],
                "rfid_uid": row['rfid_uid'],
                "designation": row['designation'],
                "status": row['status'],
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
        if insert_records:
            supabase.table('workers').insert(insert_records).execute()
            
        return CsvImportResponse(
            success=True,
            imported_count=len(insert_records),
            message=f"Successfully imported {len(insert_records)} workers."
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
