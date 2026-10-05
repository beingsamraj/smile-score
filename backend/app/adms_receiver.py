import os
from fastapi import FastAPI, Request, Response
import uvicorn
from datetime import datetime
import threading
import traceback
import requests

app = FastAPI(title="eSSL ADMS Receiver")

# Global counter and lock for thread-safe numbering
request_counter = 0
counter_lock = threading.Lock()

# Ensure capture directory exists at the project root level
# __file__ is backend/app/adms_receiver.py
# PROJECT_ROOT is backend/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(PROJECT_ROOT, "essl_captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "essl-adms-receiver"}

@app.get("/")
async def root():
    return {"status": "ok", "service": "essl-adms-receiver", "message": "Listening for ADMS push"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def catch_all(request: Request, path: str):
    global request_counter
    
    with counter_lock:
        request_counter += 1
        current_req_num = request_counter

    now = datetime.now()
    timestamp_iso = now.isoformat()
    timestamp_file = now.strftime("%Y-%m-%d_%H%M%S")
    
    client_ip = request.client.host if request.client else "Unknown"
    method = request.method
    full_path = request.url.path
    query_params = dict(request.query_params)
    headers = dict(request.headers)
    content_type = headers.get("content-type", "<None>")
    
    try:
        raw_body = await request.body()
    except Exception as e:
        raw_body = b""
        print(f"Error reading body: {e}")

    body_size = len(raw_body)
    
    try:
        decoded_body = raw_body.decode('utf-8')
    except UnicodeDecodeError:
        decoded_body = f"<Binary Data or Decode Error: {repr(raw_body)}>"

    # ====================================================
    # 1. SAVE RAW REQUEST TO DISK FIRST
    # ====================================================
    filename = f"request_{current_req_num:06d}_{timestamp_file}.txt"
    filepath = os.path.join(CAPTURE_DIR, filename)
    
    file_content = []
    file_content.append("=" * 60)
    file_content.append("eSSL ADMS RAW REQUEST")
    file_content.append("=====================\n")
    
    file_content.append(f"Request Number: {current_req_num}")
    file_content.append(f"Timestamp: {timestamp_iso}")
    file_content.append(f"Client IP: {client_ip}")
    file_content.append(f"Method: {method}")
    file_content.append(f"Path: {full_path}")
    file_content.append(f"Body Size: {body_size} bytes\n")
    
    file_content.append("Query Parameters:")
    if query_params:
        for k, v in query_params.items():
            file_content.append(f"{k}={v}")
    else:
        file_content.append("<None>")
    file_content.append("")
    
    file_content.append("Headers:")
    for k, v in headers.items():
        file_content.append(f"{k}: {v}")
    file_content.append("")
    
    file_content.append("RAW BODY:")
    if decoded_body and not decoded_body.startswith("<Binary"):
        file_content.append(decoded_body)
    elif raw_body:
        file_content.append(repr(raw_body))
    else:
        file_content.append("<Empty Body>")
    file_content.append("\n" + "=" * 60)
    file_content.append("END REQUEST")
    file_content.append("===========\n")
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(file_content))
    except Exception as e:
        print(f"FAILED TO SAVE CAPTURE FILE: {e}")

    # ====================================================
    # 2. ATTEMPT PARSING AND MAPPING (Safely)
    # ====================================================
    essl_id = None
    mapped_worker = None
    parser_error = None
    mapping_error = None

    try:
        from app.services.essl_parser import parse_adms_request
        from app.services.active_worker import map_essl_to_worker
        
        parsed = parse_adms_request(method, full_path, query_params, decoded_body if not decoded_body.startswith("<Binary") else "")
        essl_id = parsed.get("essl_user_id")
        
        if essl_id:
            mapped_worker = map_essl_to_worker(essl_id)
            if mapped_worker:
                try:
                    # Notify main FastAPI application to set current worker
                    requests.post(
                        "http://127.0.0.1:8000/api/test/active-worker",
                        json={"worker_id": mapped_worker, "essl_user_id": essl_id},
                        timeout=2
                    )
                except Exception as req_e:
                    mapping_error = f"HTTP POST to main API failed: {req_e}"
    except Exception as parse_e:
        parser_error = str(parse_e)
        traceback.print_exc()

    # ====================================================
    # 3. PRINT TO TERMINAL
    # ====================================================
    print("\n========================================")
    print("eSSL ADMS REQUEST")
    print("=================")
    print(f"Request Number: {current_req_num}")
    print(f"Timestamp:      {timestamp_iso}")
    print(f"Client IP:      {client_ip}")
    print(f"Method:         {method}")
    print(f"Path:           {full_path}")
    print(f"Content-Type:   {content_type}")
    print(f"Body Size:      {body_size} bytes")
    
    query_str = "&".join([f"{k}={v}" for k, v in query_params.items()]) if query_params else "<None>"
    print(f"Query:          {query_str}")
    
    print("\nBody:")
    if decoded_body and not decoded_body.startswith("<Binary"):
        print(decoded_body[:500] + ("...\n[TRUNCATED IN TERMINAL - SEE CAPTURE FILE]" if len(decoded_body) > 500 else ""))
    elif raw_body:
        print(repr(raw_body)[:500] + "...")
    else:
        print("<Empty Body>")
        
    print(f"\n---> Parsed eSSL ID: {essl_id}")
    print(f"---> Mapped Worker:  {mapped_worker}")
    if parser_error:
        print(f"!!! Parser Error: {parser_error}")
    if mapping_error:
        print(f"!!! Mapping Error: {mapping_error}")
        
    print(f"Capture saved to: {filepath}")
    print("=====\n")

    # Always return HTTP 200 OK so the eSSL device doesn't error out
    return Response(content="OK", status_code=200, media_type="text/plain")

if __name__ == "__main__":
    print("==================================================")
    print("Starting eSSL ADMS Debug Receiver on 0.0.0.0:8081...")
    print(f"Capture directory: {os.path.abspath(CAPTURE_DIR)}")
    print("Waiting for ADMS device to connect...")
    print("==================================================")
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="error")
