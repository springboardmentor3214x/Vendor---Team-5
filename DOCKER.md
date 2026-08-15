# Docker development

1. Copy `.env.example` to `.env`, then replace `POSTGRES_PASSWORD` and
   `SECRET_KEY` with unique values. Do not commit `.env`.
2. Start the complete stack:

   ```powershell
   docker compose up --build
   ```

3. Open the frontend at `http://localhost:4200` and the health endpoint at
   `http://localhost:4200/health`. Browser API calls use `/api` and are
   reverse-proxied by Nginx to FastAPI. PostgreSQL and FastAPI are intentionally
   not exposed as host ports.

The backend container runs Alembic migrations before starting Uvicorn. The
frontend is served by Nginx and uses the same-origin browser-side API URL
(`/api`). Uploaded files are stored in the persistent `uploads_data` volume.
