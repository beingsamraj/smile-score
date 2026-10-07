import re

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'async def run_grievance_detection\(\):.*?logger\.exception\("Grievance detection failed"\)', '', text, flags=re.DOTALL)
text = text.replace("scheduler.add_job(run_grievance_detection, 'interval', minutes=30, coalesce=True, max_instances=1)", '')

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
