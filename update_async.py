import os

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('def get_worker_timeline(worker_id: str, days: int = 7):', 'async def get_worker_timeline(worker_id: str, days: int = 7):')

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
