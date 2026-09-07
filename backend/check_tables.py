import sys
sys.path.append('e:/smile-score/backend')
from app.database import supabase

tables = ['workers', 'factories', 'devices', 'departments', 'alerts', 'risk_predictions', 'shifts']
for t in tables:
    try:
        r = supabase.table(t).select('*').limit(1).execute()
        cols = list(r.data[0].keys()) if r.data else 'empty'
        print(f'{t}: OK - cols: {cols}')
    except Exception as e:
        print(f'{t}: ERROR - {e}')
