# BrandGuard AI

BrandGuard AI is an AI-assisted brand content review and approval platform designed to help teams maintain consistent, accurate, and policy-compliant content.

The platform provides document management, automated content reviews, evidence-linked findings, correction suggestions, collaboration, brand source management, and controlled approval workflows.

## Key Features

### 1. Document Management
- Upload and manage content documents.
- Process documents asynchronously using background workers.
- Maintain document versions and processing status.
- Store files using configurable storage backends.
- Scan uploaded files using ClamAV.
- Extract text from PDF and DOCX documents.
- Support OCR for scanned PDF documents and images using Tesseract.

### 2. Content Review
- Run deterministic and contextual content checks.
- Identify potential content and brand guideline violations.
- Generate structured review findings.
- Display supporting evidence and document excerpts.
- Explain why content has been flagged.
- Track findings and their resolution status.

### 3. AI-Assisted Correction Suggestions
- Optional AI-powered correction suggestions.
- Suggested replacement text and explanations for identified issues.
- Human review of proposed corrections.
- Reviewers can accept, edit, or reject suggestions.
- AI suggestions are not automatically approved or published.
- Backend support for AI-assisted correction suggestions.
- Suggested replacement text and explanations when generation is configured.
- Human review is required before proposed corrections are used.
- AI suggestions are not automatically approved or published.

**Current limitation:** Live AI correction generation requires a configured LLM API key and available provider API credits. The complete accept/edit/reject suggestion workflow has not yet been verified in the frontend review interface.

**Note:** Live AI correction generation requires a configured LLM API key and available provider API credits. The deterministic review functionality operates independently of paid AI access. AI suggestions should be reviewed by a human before use.

### 4. Collaboration and Approvals
- User authentication and workspace management.
- Organization-scoped access.
- Team member management.
- Review comments and collaboration.
- Approval request creation and decision tracking.
- Separation of duties to prevent self-approval.
- Approval decision timestamps and audit records.

### 5. Brand Source Management
- Manage brand reference sources and guidelines.
- Track source verification status.
- Support controlled source verification workflows.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, JavaScript, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database migrations | Alembic |
| Background processing | Celery |
| Message broker | Redis |
| File storage | MinIO |
| File scanning | ClamAV |
| Document extraction | PyMuPDF, pypdf, python-docx |
| OCR | Tesseract, pytesseract |
| Deployment | Docker, Docker Compose |

## System Architecture

BrandGuard AI uses a modular frontend and backend architecture.

1. React provides the user interface.
2. FastAPI handles authentication, APIs, business logic, and document operations.
3. PostgreSQL stores application data.
4. Redis supports background task messaging.
5. Celery workers process document-processing tasks.
6. The outbox dispatcher publishes pending application events to background workers.
7. MinIO stores uploaded documents.
8. ClamAV provides antivirus scanning for uploaded files.
9. The document extraction pipeline extracts text from supported formats and uses OCR when required.
10. The review pipeline generates findings, attaches evidence, and manages correction suggestion status.
## Testing

BrandGuard AI includes automated backend tests and frontend build validation.

### Backend Tests

Run the backend test suite:

```powershell
cd backend
python -m pytest -q
```

The latest verified local test run completed with:

- **63 tests passed**
- 1 warning
- Coverage includes API behavior, document processing, review workflows, and approval organization isolation.

### Frontend Build

Run the production build:

```powershell
cd frontend
npm install
npm run build
```

The frontend production build completed successfully.

### Security Checks

The project includes automated GitHub Actions workflows for:

- Backend and frontend validation.
- Dependency security auditing.

Latest verified GitHub Actions results for commit `3ccc6fe`:

- BrandGuard AI Tests: Passed.
- BrandGuard AI Security Checks: Passed.

[GitHub Actions](https://github.com/bhagya-3/BrandGuard-AI/actions)

## Known Limitations

- **AI correction generation:** Requires a valid LLM provider API key and available API credits. The complete accept/edit/reject workflow has not yet been verified in the frontend.
- **Finding accuracy:** Automated content checks may produce false positives, especially in academic references, dates, identifiers, and bibliography sections. Findings should be reviewed by a human.
- **PDF OCR:** OCR depends on PyMuPDF and Tesseract being installed and available in the runtime environment. Native-library restrictions in some environments may prevent OCR from running.
- **External integrations:** AI generation and other optional integrations depend on correctly configured external services and credentials.
- **Human approval:** Automated findings and suggestions do not replace human review or final approval decisions.

## Roadmap

Planned improvements include:

1. Complete and test the frontend correction-suggestion workflow, including accept, edit, and reject actions.
2. Improve finding accuracy and reduce false positives in academic and structured documents.
3. Expand automated integration and end-to-end testing for document upload, review, collaboration, and approval journeys.
4. Improve OCR compatibility and document-processing reliability across environments.
5. Enhance onboarding, empty states, error messages, and reviewer guidance.
6. Expand brand guideline verification and reporting capabilities.


## Run with Docker Compose

### Prerequisites

Install the following before starting:

- Docker Desktop
- Docker Compose
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/bhagya-3/BrandGuard-AI.git
cd BrandGuard-AI
```

### 2. Configure root environment variables

Create the root environment file:

```powershell
Copy-Item .env.example .env
```

Open the root `.env` file and configure these values:

- `POSTGRES_PASSWORD`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- `JWT_SECRET_KEY`

Use strong, unique values instead of the example placeholders.

The root environment file also supports `VITE_API_BASE_URL`. Docker Compose defaults this to:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 4. Build and start the application

Run:

```powershell
docker compose up --build -d
```

Check the status of the containers:

```powershell
docker compose ps
```

Wait until the required services have started and their health checks are successful.

### 5. Apply database migrations

Database migrations do not run automatically when the backend starts. Apply them manually:

```powershell
docker compose exec backend python -m alembic upgrade head
```

Verify the current migration revision:

```powershell
docker compose exec backend python -m alembic current
```

The output should show the latest migration revision marked as `(head)`.

### 6. Access the application

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API documentation | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |

Check backend health:

```powershell
Invoke-WebRequest http://localhost:8000/health -UseBasicParsing
```

View backend logs:

```powershell
docker compose logs -f backend
```

## Local Development

Docker Compose is the recommended way to run the complete application because it starts the supporting services, including PostgreSQL, Redis, MinIO, ClamAV, Celery workers, and the outbox dispatcher.

For separate local frontend and backend development, follow the instructions below.

### Backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure the backend `.env` file for your local environment.

The example backend configuration uses SQLite and local file storage. Start any required supporting services before testing features that depend on them.

Start the backend:

```powershell
uvicorn app.main:app --reload
```

The backend runs at:

http://localhost:8000

### Frontend

Open another terminal in the project root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend runs at:

http://localhost:5173

For local frontend development, leave `VITE_API_BASE_URL` empty in `frontend/.env`. The frontend will use the current page host on port 8000 for API requests.
