import os

with open('backend/app/routers/grievances.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_logic = """    if date_filter and date_filter.lower() != 'all':
        now = datetime.now(timezone.utc)
        if date_filter == 'today':
            start_date = now.replace(hour=0, minute=0, second=0).isoformat()
        elif date_filter == '7d':
            start_date = (now - timedelta(days=7)).isoformat()
        elif date_filter == '30d':
            start_date = (now - timedelta(days=30)).isoformat()
        else:
            start_date = None
            
        if start_date:
            where_clauses.append("g.detected_at >= ?")
            params.append(start_date)"""

new_logic = """    if date_filter and date_filter.lower() != 'all':
        # If user picks a date like '2026-10-07', we match dates starting with that
        where_clauses.append("g.detected_at LIKE ?")
        params.append(f"{date_filter}%")"""

text = text.replace(old_logic, new_logic)

with open('backend/app/routers/grievances.py', 'w', encoding='utf-8') as f:
    f.write(text)
