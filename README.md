# Smile Score

Smile Score is an AI-powered worker wellbeing and emotion analytics platform. The system leverages IoT endpoints (ESP32) to capture RFID check-ins alongside realtime mood tracking (Happy, OK, Sad). Data is piped via WebSocket and REST APIs to a comprehensive Next.js dashboard where supervisors can track production risks, anomaly trends, and holistic wellness.

## Architecture
- **Backend:** FastAPI, Python, SQLite/Cloudflare D1, APScheduler, XGBoost/Prophet for predictive modeling.
- **Frontend:** Next.js 14, React, TailwindCSS, Lucide Icons, Recharts for data visualization.
- **Database:** Cloudflare D1 (Serverless SQLite).
- **IoT Integration:** Supports ESP32 with RFID RC522 modules to verify worker identity.

## Prerequisites
- Python 3.11+
- Node.js 20+
- Cloudflare Wrangler (for local database emulation)

## Environment Variables

### Backend (`backend/.env`)
```
CLOUDFLARE_API_TOKEN=your_cf_token
CLOUDFLARE_ACCOUNT_ID=your_cf_account
D1_DATABASE_ID=your_d1_database_id
USE_LOCAL_DB=True
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Quick Start

### 1. Database (Local Emulation)
```bash
cd backend
npx wrangler d1 execute smile_score --local --file=migrations/0001_initial_schema.sql
npx wrangler d1 execute smile_score --local --file=migrations/0002_seed_data.sql
```

### 2. Backend API
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000`.

## API Documentation
Once the backend is running, the OpenAPI specification is available natively:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON:** [http://localhost:8000/api/openapi](http://localhost:8000/api/openapi)

## Contributing
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes
3. Ensure CI checks (Ruff formatting, MyPy types, React linting) pass
4. Open a Pull Request

## License
MIT License

## AI/ML Features
1. **Anomaly detection**: (Production) Detects anomalies in real-time streaming data from factories.
2. **Factory forecasting**: (Production) Uses Prophet to forecast future worker wellbeing based on historical data.
3. **Production-risk prediction**: (Production) Uses XGBoost to evaluate immediate factory risk levels.
4. **Factory risk dashboard**: (Production) Aggregates factory risk computations for a real-time high-level view.
5. **Recommendations**: (Prototype) Rule-based logic providing operational wellness recommendations (NOT medical diagnosis).
6. **Multi-signal anomaly detection**: (Planned) Placeholder for future advanced sensor integrations.
7. **Emotion classification architecture**: (Baseline) Interface for raw facial/signal inputs, currently falling back to standard hardware feedbacks.

**Ethics Note**: Smile Score provides operational proxies for wellbeing. It DOES NOT provide medical diagnoses. Human review is required for all AI-guided operational decisions.
