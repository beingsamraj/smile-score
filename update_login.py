import os
import re

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_login_pattern = r'@app\.post\("/api/auth/login"\).*?(?=@app\.post|@app\.get|@app\.on_event)'
import re
match = re.search(old_login_pattern, text, re.DOTALL)
if match:
    old_login = match.group(0)
    new_login = """@app.post("/api/auth/login")
@limiter.limit("10/minute")
async def login(req: LoginRequest, request: Request):
    from app.services.d1_client import d1
    import jwt
    from datetime import datetime, timedelta, timezone
    
    try:
        # Check against local D1 users table
        # User might type email, employee_code, or just 'admin_user'
        if req.username == 'admin_user' or req.username == 'ADMIN001':
            res = await d1.execute("SELECT * FROM users WHERE employee_code = 'ADMIN001'")
        else:
            res = await d1.execute("SELECT * FROM users WHERE email = ? OR employee_code = ?", [req.username, req.username])
            
        if not res:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
            
        user = res[0]
        
        # Hardcoded password check for development
        if req.password not in ["admin123", "password"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
            
        # Role check
        if user.get("role") not in ["admin", "nurse"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ACCESS_DENIED")
            
        token = jwt.encode(
            {"sub": user.get("id"), "role": user.get("role"), "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
            "super-secret-key-12345",
            algorithm="HS256"
        )
        
        return {"user": {"id": user.get("id"), "username": user.get("employee_code"), "email": user.get("email"), "role": user.get("role")}, "token": token}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login failed")
        raise HTTPException(status_code=500, detail="Internal server error")

"""
    text = text.replace(old_login, new_login)
    with open('backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(text)
