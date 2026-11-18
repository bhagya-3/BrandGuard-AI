# BrandGuard AI

BrandGuard AI is a React workspace backed by a FastAPI service. Creators can
register, upload content, inspect review findings, comment, resolve findings,
request approval, and manage brand sources. Review and approval actions are
organization-scoped and written to the backend audit log.

## Run locally

1. Install backend dependencies and configure the API:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   uvicorn app.main:app --reload
   ```

2. In another terminal, install and start the React app:

   ```powershell
   cd frontend
   npm install
   Copy-Item .env.example .env
   npm run dev
   ```

The frontend is served at `http://localhost:5173`; the API is served at
`http://localhost:8000`. Register an account to create the first organization
and workspace. The default database and file storage are local SQLite and the
configured `FILE_STORAGE_PATH`.
The development frontend derives the API host from the page URL and uses port
`8000` with the `/api/v1` prefix. Set `VITE_API_BASE_URL` to override it.
`FRONTEND_ORIGIN` accepts comma-separated frontend origins, including both
`localhost` and `127.0.0.1` for local development.

## Local Docker demo

Copy the root `.env.example` to `.env`, replace its local-only credentials, and
start the full demo stack:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

This starts React/Nginx, FastAPI, PostgreSQL, Redis, and MinIO. The UI is at
`http://localhost:5173`, the API at `http://localhost:8000`, and MinIO console
at `http://localhost:9001`. The compose configuration is for local development;
use managed credentials, storage, TLS, and non-development secrets in
deployment.

## Configuration and integrations

Copy [`backend/.env.example`](backend/.env.example) to `backend/.env` and set
secrets before deployment. `DATABASE_URL` accepts SQLite or PostgreSQL URLs
(PostgreSQL uses `psycopg`). `STORAGE_BACKEND` supports `local`, `minio`, `s3`,
and `azure_blob`; cloud credentials and containers/buckets must be provisioned
in the corresponding provider first. The review engine runs deterministic and contextual checks by default.
Configuring `LLM_API_KEY` enables optional correction suggestions and sends
relevant review text to that external provider; do so only if this is
appropriate for your content and privacy requirements. Never commit credentials.

Image OCR uses the `pytesseract` Python package and also requires the Tesseract
OCR executable to be installed on the API host. `python-multipart` is required
for document uploads.

## Operations scripts

Run these commands from the `backend` directory so `backend/.env` and its
`DATABASE_URL` are used:

```powershell
python ..\scripts\seed_roles.py
python ..\scripts\create_admin.py --email admin@example.com --name "Workspace Admin" --organization "Example Organization"
python ..\scripts\backup_database.py
```

`create_admin.py` securely prompts for a password. For automation, pass
`--password-env ENV_VAR_NAME` and set that environment variable before running
the command; do not put passwords directly in command arguments. The backup
script supports file-backed SQLite and PostgreSQL (`pg_dump` must be installed
for PostgreSQL). Use `--output` to set the destination and `--overwrite` only
when replacing an existing backup is intended.

## Checks

```powershell
cd frontend
npm run build
npm run lint
cd ..\backend
python -m pytest
```
