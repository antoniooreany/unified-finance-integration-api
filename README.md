# Unified Finance Integration API

This is the FastAPI application for unifying finance integrations.

## Setup
1. `pip install -r requirements.txt`
2. `cp .env.example .env`
3. `uvicorn app.main:app --reload`


## Running with Docker
You can build and run the API using Docker. No provider credentials are bundled in the image; they must be provided at runtime.

```bash
docker build -t unified-finance-integration-api:latest .
docker run -d -p 8000:8000 -e PROVIDER_BASE_URL="http://localhost:5000" -e PROVIDER_API_KEY="test-api-key-not-a-secret" unified-finance-integration-api:latest
```

To verify the container is running successfully, hit the health check endpoint:
```bash
curl http://localhost:8000/health
```
