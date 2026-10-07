import os

with open('app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

task_code = """
async def run_grievance_detection():
    try:
        from app.routers.grievances import detect_grievances
        res = await detect_grievances()
        logger.info(res["message"])
    except Exception as e:
        logger.exception("Grievance detection failed")
"""

if 'run_grievance_detection' not in text:
    text = text.replace('async def run_anomaly_detection():', task_code + '\nasync def run_anomaly_detection():')
    text = text.replace("scheduler.add_job(compute_factory_risks, 'interval', minutes=60, coalesce=True, max_instances=1)", "scheduler.add_job(compute_factory_risks, 'interval', minutes=60, coalesce=True, max_instances=1)\n    scheduler.add_job(run_grievance_detection, 'interval', minutes=30, coalesce=True, max_instances=1)")
    
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(text)
