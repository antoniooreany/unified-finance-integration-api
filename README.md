# Unified Finance Integration API

Unified Finance Integration API is a robust, lightweight integration layer designed to fetch, normalize, and present financial data (e.g., invoices) from external providers. It acts as an abstraction layer for third-party billing providers.

> [!TIP]
> **🎥 Смотреть демо (Live Demo):** Посмотрите, как работает дашборд в реальном времени! Нажмите Play ниже.

<div align="center">
  <video src="docs/demo.mp4" controls width="100%" style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"></video>
</div>


## 🚀 Features
- **FastAPI Backend**: High-performance asynchronous API with automatic Swagger UI documentation.
- **Data Validation & Normalization**: Uses Pydantic for strict schema validation of provider responses.
- **Resilient Integration**: Implements proper HTTP error handling, timeout handling, and retry headers (HTTP 429) using httpx.
- **Vanilla JS Dashboard**: Lightweight, semantic frontend without heavy frameworks, utilizing native DOM APIs for performance and security.
- **Dockerized**: Ready for containerized deployment.

## 🛠 Tech Stack
- **Backend**: Python 3.12, FastAPI, Pydantic, httpx
- **Frontend**: HTML5, CSS3, Vanilla JS
- **Testing**: Pytest
- **Infrastructure**: Docker, Docker Compose

---

## ⚡ Quick Start (One-Click)

The easiest way to start the application is using Docker Compose.

`ash
# Start the API and Dashboard in the background
docker-compose up --build -d
`

Once running, navigate to [http://localhost:8000/](http://localhost:8000/) to access the dashboard!

To stop the application:
`ash
docker-compose down
`

---

## 💻 Local Development

### 1. Setup the environment
`ash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scriptsctivate
pip install -r requirements.txt
`

### 2. Configuration
Copy the sample environment file:
`ash
cp .env.example .env
`
Ensure PROVIDER_BASE_URL points to your mock/sandbox provider.

### 3. Run the API
You can run the API directly or use the provided Makefile:
`ash
make run
# OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
`

### 4. Tests
Run the test suite using pytest:
`ash
make test
# OR
pytest tests/
`

## 📊 Dashboard Overview

When the API is running, open http://localhost:8000/ in a browser. The dashboard allows users to:
1. **Sync Invoices**: Request current invoices in real-time through the POST /api/v1/sync/invoices endpoint.
2. **View Details**: Expand normalized invoices in a responsive CSS Grid layout.

*Note: The P0 Demo currently acts as a real-time proxy and does not store or persist invoice history.*
