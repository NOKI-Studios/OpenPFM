# OpenPFM

Open source print farm manager for Bambu Lab 3D printers. Self-hosted, runs on Docker.

## Overview

OpenPFM is a web-based platform for remote control, automation and management of Bambu Lab 3D printers. It provides a clean dashboard for monitoring printer status, managing filament inventory, and controlling print jobs across multiple printers.

## Info

OpenPFM is currently in active development. Please submit issues, feature requests or pull requests when you encounter problems.

## Features & Planned Features

- Remote printer control (start, stop, pause, resume, home, light)
- Real-time printer status monitoring
- Filament inventory management with low-stock alerts
- AMS / multi-material system tracking
- File management via FTP
- Slicing via OrcaSlicer CLI
- Automation and remote control via n8n
- User management with role-based access
- Dark and light mode
- Localisation

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, shadcn-vue, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Automation | n8n |
| Slicer | OrcaSlicer (headless) |
| Infrastructure | Docker, Docker Compose |

## Supported Hardware

- Bambu Lab A1
- Bambu Lab A1 mini
- Bambu Lab P1P
- Bambu Lab P1S
- Bambu Lab X1C
- Bambu Lab X1E

AMS, AMS Lite and AMS Hub are supported.

## Requirements

- Docker
- Docker Compose
- A Bambu Lab printer on the same local network

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/NOKI-Studios/OpenPFM.git
cd OpenPFM
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
DB_USER=openpfm
DB_PASSWORD=your_password
DB_NAME=openpfm
N8N_USER=admin
N8N_PASSWORD=your_password
```

**3. Start the stack**

```bash
docker compose up -d
```

**4. Access the application**

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| n8n | http://localhost:5678 |

**5. Add your first printer**

Open the frontend, navigate to Drucker and add your Bambu Lab printer with its IP address and access code.

The access code can be found in the Bambu Lab app under your printer settings.

## Project Structure

```
OpenPFM/
├── backend/
│   ├── src/
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routers/       # FastAPI endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── scripts/       # Bambu printer control scripts
│   │   └── services/      # Business logic
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/           # Axios API clients
│   │   ├── components/    # Vue components
│   │   ├── types/         # TypeScript types
│   │   └── views/         # Page views
│   └── Dockerfile
├── slicer/
│   └── Dockerfile         # OrcaSlicer headless container
├── n8n/                   # n8n data volume
└── docker-compose.yml
```

## API

The REST API is documented via Swagger UI at `http://localhost:8000/docs`.

Main endpoint groups:

- `GET/POST/PATCH/DELETE /printers` — printer management
- `GET/POST /printers/{id}/status` — live status
- `POST /printers/{id}/print` — start a print job
- `POST /printers/{id}/stop` — stop print
- `POST /printers/{id}/pause` — pause print
- `POST /printers/{id}/resume` — resume print
- `POST /printers/{id}/home` — home axes
- `POST /printers/{id}/light` — control work light
- `GET/POST/DELETE /printers/{id}/files` — file management
- `POST /printers/{id}/upload` — upload file via FTP
- `GET/POST/PATCH/DELETE /filaments` — filament types
- `GET/POST/PATCH/DELETE /filaments/{id}/spools` — spool inventory
- `GET/POST/PATCH/DELETE /users` — user management

## Contributing

Pull requests are welcome. For larger changes, please open an issue first.

## License

MIT
