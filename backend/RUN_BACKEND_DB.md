# Run VendorIQ backend and PostgreSQL locally

In Windows PowerShell, from the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
psql -U postgres -h localhost -c "CREATE DATABASE vendor_db;"
alembic upgrade head
python seed_data.py
python scripts/smoke_test_backend_db.py
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for FastAPI Swagger UI. Edit `.env` if your PostgreSQL credentials differ; never commit it. If the database already exists, omit the `psql` command.
