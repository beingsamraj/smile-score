import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Ensure we load from the exact .env file in the backend directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path, override=True)

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SECRET_KEY", "")

print(f"Supabase URL: {url}")
print(f"Secret Key loaded: {'Yes' if key and key != 'YOUR_SECRET_KEY' else 'No'} (length: {len(key)})")

supabase: Client = create_client(url, key)
