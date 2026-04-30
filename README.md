# OpenPFM

Open source print farm manager for Bambu Lab 3D printers. Self-hosted, runs on Docker.

## Overview

OpenPFM is a web-based platform for remote control, automation and management of Bambu Lab 3D printers. It provides a clean dashboard for monitoring printer status, managing filament inventory, and controlling print jobs across multiple printers.

Your Bambu printer (in my case the A1) needs to be on firmware 01.04 and in lan only mode. Keep in mind that bambu handy wont work in lan only mode. You can still upgrade to the newest firmware, but expect some features to not work due to changes. Firmware 01.04 works the best and is actively being tested. 
Check out downgrading here: [BambuLab Wiki](https://wiki.bambulab.com/en/knowledge-sharing/firmware-downgrade)

## Info

OpenPFM is currently in active development. Please submit issues, feature requests or pull requests when you encounter problems.

## Features & Planned Features

- Remote printer control (start, stop, pause, resume, home, light)
- Real-time printer status monitoring
- Camera streaming
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
| Slicer | OrcaSlicer (headless, in a Ubuntu environment) |
| Infrastructure | Docker, Docker Compose |

## Supported Hardware

- Bambu Lab A1
- Bambu Lab A1 mini
- Bambu Lab P1P
- Bambu Lab P1S
- Bambu Lab X1C
- Bambu Lab X1E

AMS, AMS Lite and AMS Hub are supported.

The currently tested hardware is the Bambu a1, as i dont have other printers.

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


## API

The REST API is documented via Swagger UI at `http://localhost:8000/docs`.

### Authenticating in Swagger UI

Click the **Authorize** button in the top right of the Swagger UI. A dialog will appear with the following fields:

| Field | Value |
|---|---|
| `username` | Your email address |
| `password` | Your password |
| `client_id` | Leave empty |
| `client_secret` | Leave empty |

> **Note:** The `client_id` and `client_secret` fields are shown by Swagger UI by default for OAuth2 password flows, but are not used by this API. You can safely leave them blank.

After clicking **Authorize**, all subsequent requests in the Swagger UI will include your Bearer token automatically.

## Contributing

Pull requests are welcome. For larger changes, please open an issue first.

## License

MIT