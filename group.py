import os

with open('backend/app/routers/grievances.py', 'r', encoding='utf-8') as f:
    text = f.read()

sql_block = """    sql = f\"\"\"
        SELECT 
            f.event_id as grievance_id, f.employee_id, 'NEW' as grievance_status, 
            'Direct SAD Feedback' as trigger_reason, f.timestamp as detected_at,
            e.employee_name, e.department, e.workstation,
            'SAD' as latest_feedback,
            (SELECT COUNT(*) FROM feedback_events f2 WHERE f2.employee_id = f.employee_id AND f2.feedback = 'SAD') as total_sad_count,
            f.timestamp as last_sad_time,
            (SELECT risk_level FROM ml_predictions m WHERE m.employee_id = f.employee_id ORDER BY created_at DESC LIMIT 1) as risk_level,
            (SELECT risk_score FROM ml_predictions m WHERE m.employee_id = f.employee_id ORDER BY created_at DESC LIMIT 1) as risk_score
        FROM feedback_events f
        JOIN employees e ON f.employee_id = e.employee_id
        {where_sql}
        ORDER BY f.timestamp DESC
        LIMIT ? OFFSET ?
    \"\"\""""

new_sql_block = """    # Group by employee to show SAD *people*, using the most recent SAD event as the grievance_id
    sql = f\"\"\"
        SELECT 
            MAX(f.event_id) as grievance_id, 
            f.employee_id, 
            'NEW' as grievance_status, 
            'Direct SAD Feedback' as trigger_reason, 
            MAX(f.timestamp) as detected_at,
            e.employee_name, 
            e.department, 
            e.workstation,
            'SAD' as latest_feedback,
            COUNT(f.event_id) as total_sad_count,
            MAX(f.timestamp) as last_sad_time,
            (SELECT risk_level FROM ml_predictions m WHERE m.employee_id = f.employee_id ORDER BY created_at DESC LIMIT 1) as risk_level,
            (SELECT risk_score FROM ml_predictions m WHERE m.employee_id = f.employee_id ORDER BY created_at DESC LIMIT 1) as risk_score
        FROM feedback_events f
        JOIN employees e ON f.employee_id = e.employee_id
        {where_sql}
        GROUP BY f.employee_id
        ORDER BY MAX(f.timestamp) DESC
        LIMIT ? OFFSET ?
    \"\"\""""

text = text.replace(sql_block, new_sql_block)

count_sql = """    count_sql = f\"\"\"
        SELECT COUNT(*) as c 
        FROM feedback_events f 
        JOIN employees e ON f.employee_id = e.employee_id 
        {where_sql}
    \"\"\""""

new_count_sql = """    count_sql = f\"\"\"
        SELECT COUNT(DISTINCT f.employee_id) as c 
        FROM feedback_events f 
        JOIN employees e ON f.employee_id = e.employee_id 
        {where_sql}
    \"\"\""""

text = text.replace(count_sql, new_count_sql)

with open('backend/app/routers/grievances.py', 'w', encoding='utf-8') as f:
    f.write(text)
