# Contributing to OpenPFM

## Development Setup

**Prerequisites**

- Docker and Docker Compose
- Node.js 20+
- Python 3.12+

**Clone and start**

```bash
git clone https://github.com/NOKI-Studios/OpenPFM.git
cd OpenPFM
cp .env.example .env
docker compose up -d db n8n slicer
```

**Backend (local)**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**Frontend (local)**

```bash
cd frontend
npm install
npm run dev
```

## Conventions

**Branches**

- `main` — stable
- `feat/description` — new features
- `fix/description` — bug fixes

**Commit messages**

Follow conventional commits:

```
feat: add websocket support for live printer status
fix: correct CORS origin for local development
chore: update dependencies
```

**Backend**

- One router file per resource
- Pydantic schemas for all request/response bodies
- Services layer for business logic, keep routers thin

**Frontend**

- One view file per page
- API calls only through `src/api/` modules
- shadcn-vue components only, no custom CSS

## Reporting Issues

Please include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Docker and OS version
