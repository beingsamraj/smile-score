import os

with open('backend/app/routers/grievances.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_sig = """async def get_grievances(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    date_filter: Optional[str] = Query("all"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):"""

new_sig = """async def get_grievances(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    date_filter: Optional[str] = Query("all"),
    risk_level: Optional[str] = Query("ALL"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):"""

old_logic = """    if date_filter and date_filter.lower() != 'all':
        where_clauses.append("f.timestamp LIKE ?")
        params.append(f"{date_filter}%")"""

new_logic = """    if date_filter and date_filter.lower() != 'all':
        where_clauses.append("f.timestamp LIKE ?")
        params.append(f"{date_filter}%")
        
    if risk_level and risk_level.upper() != 'ALL':
        where_clauses.append("(SELECT risk_level FROM ml_predictions m WHERE m.employee_id = f.employee_id ORDER BY created_at DESC LIMIT 1) = ?")
        params.append(risk_level.upper())"""

text = text.replace(old_sig, new_sig)
text = text.replace(old_logic, new_logic)

with open('backend/app/routers/grievances.py', 'w', encoding='utf-8') as f:
    f.write(text)
