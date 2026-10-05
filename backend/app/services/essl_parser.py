import re

def parse_adms_request(method: str, path: str, query_params: dict, decoded_body: str):
    """
    Attempts to extract essl_user_id, timestamp, and event_type from a raw ADMS request.
    Defensive parser that falls back gracefully.
    """
    result = {
        "essl_user_id": None,
        "timestamp": None,
        "event_type": None
    }
    
    # 1. Try to find PIN=... or USERID=... in query parameters
    for k, v in query_params.items():
        k_upper = k.upper()
        if k_upper in ["PIN", "USERID", "USER_ID", "ID"]:
            result["essl_user_id"] = str(v).strip()
            
    # 2. If not in query, try to parse the body
    if not result["essl_user_id"] and decoded_body:
        # Check for typical tab/space separated attendance log lines:
        # Example: 123 2026-09-09 10:30:00 1 0
        # Often sent in OPERLOG or ATTLOG lines
        lines = decoded_body.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Form-encoded check inside body
            if "PIN=" in line.upper() or "USERID=" in line.upper():
                pairs = line.split('&')
                for p in pairs:
                    if '=' in p:
                        k, v = p.split('=', 1)
                        if k.upper() in ["PIN", "USERID"]:
                            result["essl_user_id"] = v.strip()
                            break
                            
            # Whitespace separated check (ID Time ...)
            elif "\t" in line or " " in line:
                parts = re.split(r'\s+', line)
                # If first part is a number or alphanumeric ID
                if parts[0].isalnum():
                    result["essl_user_id"] = parts[0]
                    # Try to extract timestamp if parts look like date time
                    if len(parts) >= 3 and "-" in parts[1] and ":" in parts[2]:
                        result["timestamp"] = f"{parts[1]} {parts[2]}"
            
            if result["essl_user_id"]:
                break
                
    return result
