# Task Manager API
REST API using FastAPI and SQLite: create, list, update, and delete tasks. Includes request validation and interactive API docs.

## Run on Windows
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

Endpoints: `GET /health`, `GET /tasks`, `POST /tasks`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}`. Example body: `{"title":"Learn FastAPI","description":"Build an API"}`.

Upgrade ideas: authentication, pagination, migrations, rate limiting, and automated tests. Do not expose sensitive data without appropriate security.
