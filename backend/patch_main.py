import os

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix CORS
content = content.replace('allow_origins=["*"]', 'allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]')

# Fix Auth
auth_block_old = """        # Check user_pin
        if user.get("user_pin") != req.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")"""

auth_block_new = """        # Check user_pin
        import bcrypt
        import jwt
        from datetime import datetime, timedelta, timezone
        
        stored_pin = str(user.get("user_pin"))
        is_valid = False
        try:
            if stored_pin.startswith("$2b$") or stored_pin.startswith("$2a$"):
                is_valid = bcrypt.checkpw(req.password.encode('utf-8'), stored_pin.encode('utf-8'))
            else:
                is_valid = (stored_pin == req.password)
        except Exception:
            pass
            
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
            
        token = jwt.encode(
            {"sub": str(user.get("user_id")), "role": user.get("user_role"), "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
            "SMILE_SCORE_SECRET_JWT_KEY_SUPER_SECURE",
            algorithm="HS256"
        )"""

content = content.replace(auth_block_old, auth_block_new)
content = content.replace('"user_role": user.get("user_role"),', '"user_role": user.get("user_role"),\n                "token": token,')

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Auth patched")
