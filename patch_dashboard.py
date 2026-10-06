import re

with open('backend/app/routers/dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """@router.get("/smile-forecast")
async def get_smile_forecast(hours: int = 12):
    try:
        from app.routers.ai_features import get_factory_forecast
        # Default to FAC001 if no factory context exists in dashboard overview
        res = await get_factory_forecast("FAC001", hours)
        return {"data": res["forecast"]}
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Smile forecast failed: {e}")
        return {"data": []}
"""

text = re.sub(r'@router\.get\("/smile-forecast"\)\nasync def get_smile_forecast\(hours: int = 12\):\n    return \{"data": \[\]\}', replacement, text)

with open('backend/app/routers/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)
