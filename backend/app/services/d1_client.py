import httpx
import os
import aiosqlite
import glob
from typing import List, Dict, Any, Optional

# We will move these to .env later, but setting defaults for now based on your input
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "") 
D1_DATABASE_ID = os.getenv("D1_DATABASE_ID", "")

# Set this to False in production
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "True").lower() in ("true", "1", "yes")

class D1Client:
    def __init__(self):
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{D1_DATABASE_ID}/query"
        self.headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.local_db_path = self._find_local_db()
        
    def _find_local_db(self):
        # Find the wrangler local sqlite db
        search_path = os.path.join(os.getcwd(), ".wrangler", "state", "v3", "d1", "miniflare-D1DatabaseObject", "*.sqlite")
        files = glob.glob(search_path)
        # Exclude metadata.sqlite
        db_files = [f for f in files if "metadata" not in f]
        return db_files[0] if db_files else None

    async def execute(self, sql: str, params: list = None) -> List[Dict[str, Any]]:
        if USE_LOCAL_DB and self.local_db_path:
            return await self._execute_local(sql, params)
        else:
            return await self._execute_remote(sql, params)
            
    async def _execute_local(self, sql: str, params: list = None) -> List[Dict[str, Any]]:
        # D1 query params in API use ?, local aiosqlite uses ?
        async with aiosqlite.connect(self.local_db_path) as db:
            db.row_factory = aiosqlite.Row
            # A trick to emulate D1's returned JSON
            # Replace ? with ? inside execute
            cursor = await db.execute(sql, params or [])
            await db.commit()
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
            
    async def _execute_remote(self, sql: str, params: list = None) -> List[Dict[str, Any]]:
        if not CLOUDFLARE_ACCOUNT_ID:
            raise ValueError("Cloudflare Account ID is missing! Cannot execute query.")
            
        payload = {
            "sql": sql,
            "params": params or []
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                raise Exception(f"D1 Query Failed: {data.get('errors')}")
                
            return data["result"][0].get("results", [])

d1 = D1Client()
