import threading
import time
from datetime import datetime, timezone, timedelta

class ActiveWorkerState:
    def __init__(self):
        self.lock = threading.Lock()
        self.active_worker_id = None
        self.essl_employee_id = None
        self.authenticated_at = None
        self.expires_at = None

    def set_active_worker(self, essl_id: str, worker_id: str, timeout_seconds: int = 120):
        with self.lock:
            now = datetime.now(timezone.utc)
            self.essl_employee_id = essl_id
            self.active_worker_id = worker_id
            self.authenticated_at = now.isoformat()
            self.expires_at = (now + timedelta(seconds=timeout_seconds)).isoformat()

    def get_active_worker(self):
        with self.lock:
            if not self.active_worker_id or not self.expires_at:
                return None
            
            # Check expiration
            now = datetime.now(timezone.utc)
            expires = datetime.fromisoformat(self.expires_at)
            if now > expires:
                self._clear_unsafe()
                return None
            
            return {
                "active": True,
                "worker_id": self.active_worker_id,
                "essl_employee_id": self.essl_employee_id,
                "authenticated_at": self.authenticated_at,
                "expires_at": self.expires_at
            }

    def clear_active_worker(self):
        with self.lock:
            self._clear_unsafe()

    def _clear_unsafe(self):
        self.active_worker_id = None
        self.essl_employee_id = None
        self.authenticated_at = None
        self.expires_at = None

# Global Singleton
active_worker_service = ActiveWorkerState()

# Temporary isolated mapping until we inspect real eSSL payloads
# eSSL User ID -> Application Worker ID
MOCK_WORKER_MAPPING = {
    "123": "W001",
    "1": "W001",
    "2": "W002"
}

def map_essl_to_worker(essl_id: str) -> str:
    """Maps an eSSL employee ID to our Supabase worker_id."""
    # Fallback: if it's already a Wxxx format, use it directly
    if essl_id.startswith("W"):
        return essl_id
    # Otherwise use mock mapping
    return MOCK_WORKER_MAPPING.get(essl_id)
