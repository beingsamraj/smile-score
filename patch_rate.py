import os

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

handler = """
from fastapi.responses import JSONResponse

def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "rate limit exceeded", "detail": str(exc)},
    )
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
app.state.limiter = limiter
"""

text = text.replace('app = FastAPI(title="Smile Score API")', 'app = FastAPI(title="Smile Score API")\n' + handler)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
