# Water & Electricity Monitor — Backend

## Setup

1. Create PostgreSQL database `monitor_db` and update `backend/.env`:

   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/monitor_db
   POLL_INTERVAL_SECONDS=30
   ```

2. Install dependencies:

   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Open **http://127.0.0.1:8000/** in your browser (serves the frontend + API).

Migrations run automatically on startup.

## API

| Endpoint | Description |
|----------|-------------|
| `GET /events` | SSE stream (`water` / `electricity` status changes) |
| `GET /water/records` | Paginated water history |
| `GET /water/records/latest` | Latest water record |
| `GET /water/status` | Current level `0–3` |
| `GET /electricity/records` | Paginated electricity history |
| `GET /electricity/records/latest` | Latest electricity record |
| `GET /electricity/status` | Current on/off |

## Sensor stubs

Edit `sensors.py` to connect real hardware.
