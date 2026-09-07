import sys

with open("e:/smile-score/backend/app/routers/dashboard.py", "r", encoding="utf-8") as f:
    content = f.read()

new_overview = """
@router.get("/overview")
def get_overview():
    return {
        "active_workers": 2,
        "overall_smile_score": 4.2,
        "happy_percentage": 60,
        "ok_percentage": 30,
        "sad_percentage": 10,
        "production_risk": {"level": "LOW", "confidence": 0.9}
    }

"""

import re
content = re.sub(r'@router\.get\("/overview"\).*?def get_overview\(\):.*?(?=@router\.get\("/smile-trend"\))', new_overview, content, flags=re.DOTALL)

with open("e:/smile-score/backend/app/routers/dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)
