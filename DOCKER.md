# Docker development

1. Copy `.env.example` to `.env` only if the defaults need changing.
2. Start the complete stack:

   ```powershell
   docker compose up --build
   ```

3. Open the frontend at `http://localhost:4200`, the API docs at
   `http://localhost:8000/docs`, and the health endpoint at
   `http://localhost:8000/health`.

The backend container runs Alembic migrations before starting Uvicorn. The
frontend is served by Nginx and uses the existing browser-side API URL
(`http://localhost:8000`).
