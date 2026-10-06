with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

logging_setup = """
import logging
from pythonjsonlogger import jsonlogger
import uuid

# Configure JSON Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Clear existing handlers
if logger.hasHandlers():
    logger.handlers.clear()
    
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info("Request started", extra={"request_id": request_id, "method": request.method, "url": str(request.url)})
    response = await call_next(request)
    logger.info("Request completed", extra={"request_id": request_id, "status_code": response.status_code})
    return response
"""

if 'jsonlogger' not in content:
    content = content.replace('app = FastAPI(title="Smile Score API")', 'app = FastAPI(title="Smile Score API")\n' + logging_setup)
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
