from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.database import supabase
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
import uuid
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

def map_db_user_to_response(user_data: dict, factory_name: Optional[str] = None) -> dict:
    # Handle missing fields carefully just in case
    return {
        "id": user_data.get("user_id", ""),
        "auth_user_id": user_data.get("auth_user_id"),
        "employee_code": user_data.get("employee_code") or user_data.get("user_id", ""),
        "full_name": user_data.get("full_name") or user_data.get("username", "Unknown"),
        "email": user_data.get("email"),
        "phone": user_data.get("phone"),
        "role": user_data.get("user_role", "worker"),
        "factory_id": user_data.get("factory_id"),
        "factory_name": factory_name,
        "rfid_uid": user_data.get("rfid_uid"),
        "status": "active" if user_data.get("status") is True else "inactive",
        "created_at": user_data.get("created_at"),
        "updated_at": user_data.get("updated_at") or user_data.get("created_at")
    }

@router.get("", response_model=UserListResponse)
def get_users(
    search: Optional[str] = None,
    factory_id: Optional[str] = None,
    role: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        query = supabase.table("users").select("*")
        
        if factory_id:
            query = query.eq("factory_id", factory_id)
        if role:
            query = query.eq("user_role", role)
        if status_filter:
            db_status = True if status_filter.lower() == "active" else False
            query = query.eq("status", db_status)
            
        # Execute query
        res = query.execute()
        
        users_data = res.data or []
        
        # In-memory search (since Supabase select doesn't easily do cross-column ilike in python client)
        if search:
            search_lower = search.lower()
            users_data = [
                u for u in users_data
                if (u.get("full_name") and search_lower in u["full_name"].lower()) or
                   (u.get("employee_code") and search_lower in u["employee_code"].lower()) or
                   (u.get("email") and search_lower in u["email"].lower()) or
                   (u.get("rfid_uid") and search_lower in u["rfid_uid"].lower())
            ]
            
        # Pagination
        total = len(users_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = users_data[start:end]
        
        # Fetch factory names
        factory_ids = list(set([u.get("factory_id") for u in paginated_data if u.get("factory_id")]))
        factory_map = {}
        if factory_ids:
            fac_res = supabase.table("factories").select("factory_id, factory_name").in_("factory_id", factory_ids).execute()
            for fac in (fac_res.data or []):
                factory_map[fac["factory_id"]] = fac["factory_name"]
                
        response_data = []
        for u in paginated_data:
            fac_name = factory_map.get(u.get("factory_id"))
            response_data.append(map_db_user_to_response(u, fac_name))
            
        return {
            "data": response_data,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    try:
        res = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        user_data = res.data[0]
        
        factory_name = None
        if user_data.get("factory_id"):
            fac_res = supabase.table("factories").select("factory_name").eq("factory_id", user_data["factory_id"]).execute()
            if fac_res.data:
                factory_name = fac_res.data[0]["factory_name"]
                
        return map_db_user_to_response(user_data, factory_name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    try:
        # Check uniqueness of rfid_uid
        if user.rfid_uid:
            res = supabase.table("users").select("user_id").eq("rfid_uid", user.rfid_uid).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="RFID UID already exists")
                
        # Validate factory
        if user.factory_id:
            res = supabase.table("factories").select("factory_id").eq("factory_id", user.factory_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Factory not found")
                
        new_user_id = "U" + uuid.uuid4().hex[:8].upper()
        emp_code = "EMP-" + uuid.uuid4().hex[:6].upper()
        
        new_user = {
            "user_id": new_user_id,
            "username": user.email.split("@")[0] if user.email else new_user_id, # Fallback username for login compatibility
            "user_pin": "1234", # Default pin for login compatibility
            "user_role": user.role,
            "factory_id": user.factory_id,
            "status": True if user.status.lower() == "active" else False,
            "employee_code": emp_code,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "rfid_uid": user.rfid_uid,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        res = supabase.table("users").insert(new_user).execute()
        
        # Return response
        return get_user(new_user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UserUpdate):
    try:
        # Check if user exists
        existing = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Check uniqueness of rfid_uid if it changed
        if user.rfid_uid and user.rfid_uid != existing.data[0].get("rfid_uid"):
            res = supabase.table("users").select("user_id").eq("rfid_uid", user.rfid_uid).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="RFID UID already exists")
                
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if user.full_name is not None:
            update_data["full_name"] = user.full_name
        if user.email is not None:
            update_data["email"] = user.email
        if user.phone is not None:
            update_data["phone"] = user.phone
        if user.role is not None:
            update_data["user_role"] = user.role
        if user.factory_id is not None:
            update_data["factory_id"] = user.factory_id
        if user.rfid_uid is not None:
            update_data["rfid_uid"] = user.rfid_uid
        if user.status is not None:
            update_data["status"] = True if user.status.lower() == "active" else False
            
        supabase.table("users").update(update_data).eq("user_id", user_id).execute()
        
        return get_user(user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    try:
        # Instead of hard delete, deactivate
        existing = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        update_data = {
            "status": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("users").update(update_data).eq("user_id", user_id).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import File, UploadFile
from app.schemas.import_schemas import CsvValidationPreview, CsvRowError, CsvImportResponse
import csv
import io

def parse_and_validate_csv(file_content: str):
    reader = csv.DictReader(io.StringIO(file_content))
    expected_headers = ['full_name', 'email', 'phone', 'role', 'factory_code', 'rfid_uid', 'status']
    
    # Check if all headers are exactly present or map to lower
    actual_headers = [h.strip().lower() for h in reader.fieldnames or []]
    
    missing_headers = [h for h in expected_headers if h not in actual_headers]
    if missing_headers:
        raise ValueError(f"Invalid CSV headers. Missing: {', '.join(missing_headers)}")

    # Fetch all factories to map factory_code to factory_id
    fac_res = supabase.table('factories').select('factory_id').execute()
    existing_factory_ids = {f['factory_id'] for f in fac_res.data or []}
    
    # Fetch existing RFIDs and Emails
    users_res = supabase.table('users').select('rfid_uid, email').execute()
    existing_rfids = {u['rfid_uid'] for u in users_res.data or [] if u.get('rfid_uid')}
    existing_emails = {u['email'].lower() for u in users_res.data or [] if u.get('email')}
    
    csv_rfids = set()
    csv_emails = set()

    total_rows = 0
    errors = []
    valid_rows = 0
    parsed_data = []

    for idx, row in enumerate(reader, start=2): # Header is 1
        total_rows += 1
        row_errors = []
        
        # Normalize keys and values
        norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
        
        full_name = norm_row.get('full_name')
        email = norm_row.get('email')
        phone = norm_row.get('phone')
        role = norm_row.get('role', '').lower()
        factory_code = norm_row.get('factory_code')
        rfid_uid = norm_row.get('rfid_uid')
        status = norm_row.get('status', 'active').lower()

        if not full_name:
            row_errors.append('Full name is required.')
            
        if email:
            email_lower = email.lower()
            if email_lower in existing_emails:
                row_errors.append(f"Email {email} is already in use in database.")
            if email_lower in csv_emails:
                row_errors.append(f"Email {email} is duplicated in the uploaded CSV.")
            csv_emails.add(email_lower)
            
        if role != 'worker':
            row_errors.append(f"Invalid role '{role}'. Only 'worker' role is allowed for bulk import.")
            
        if factory_code:
            if factory_code not in existing_factory_ids:
                row_errors.append(f"Factory code {factory_code} does not exist.")
                
        if rfid_uid:
            rfid_norm = rfid_uid.upper().replace(' ', '')
            if rfid_norm in existing_rfids:
                row_errors.append(f"RFID UID {rfid_norm} is already assigned in database.")
            if rfid_norm in csv_rfids:
                row_errors.append(f"RFID UID {rfid_norm} is duplicated in the uploaded CSV.")
            csv_rfids.add(rfid_norm)
            norm_row['rfid_uid'] = rfid_norm
            
        if status not in ['active', 'inactive']:
            row_errors.append(f"Invalid status '{status}'. Must be active or inactive.")
            
        if row_errors:
            errors.append(CsvRowError(row=idx, errors=row_errors))
        else:
            valid_rows += 1
            parsed_data.append({
                'full_name': full_name,
                'email': email or None,
                'phone': phone or None,
                'role': 'worker',
                'factory_code': factory_code or None,
                'rfid_uid': norm_row.get('rfid_uid') or None,
                'status': status
            })
            
    if total_rows == 0:
        raise ValueError('CSV contains no user records.')
        
    return {
        'valid': len(errors) == 0,
        'total_rows': total_rows,
        'valid_rows': valid_rows,
        'invalid_rows': len(errors),
        'errors': errors,
        'parsed_data': parsed_data
    }

@router.post("/import/validate", response_model=CsvValidationPreview)
async def validate_users_import(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .csv files are supported.")
        
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="CSV file is too large. Maximum allowed size is 5 MB.")
        
    try:
        decoded_content = content.decode('utf-8-sig')
        result = parse_and_validate_csv(decoded_content)
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
async def import_users(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .csv files are supported.")
        
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="CSV file is too large. Maximum allowed size is 5 MB.")
        
    try:
        decoded_content = content.decode('utf-8-sig')
        result = parse_and_validate_csv(decoded_content)
        
        if not result['valid']:
            raise HTTPException(status_code=400, detail="CSV contains validation errors. Please fix them before importing.")
            
        if result['total_rows'] > 5000:
            raise HTTPException(status_code=400, detail="CSV contains too many rows. Maximum allowed rows: 5000.")
            
        parsed_data = result['parsed_data']
        insert_records = []
        
        for row in parsed_data:
            new_user_id = "U" + uuid.uuid4().hex[:5].upper()
            emp_code = "EMP-" + uuid.uuid4().hex[:6].upper()
            
            insert_records.append({
                "user_id": new_user_id,
                "username": row['email'] or new_user_id,
                "user_pin": "1234",
                "user_role": "worker",
                "factory_id": row['factory_code'],
                "status": True if row['status'] == 'active' else False,
                "employee_code": emp_code,
                "full_name": row['full_name'],
                "email": row['email'],
                "phone": row['phone'],
                "rfid_uid": row['rfid_uid'],
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
        if insert_records:
            supabase.table('users').insert(insert_records).execute()
            
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
