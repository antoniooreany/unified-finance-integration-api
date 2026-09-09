.PHONY: help install run test lint format docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run local development server"
	@echo "  make test       - Run tests"
	@echo "  make docker-up  - Start application using Docker Compose and open browser"
	@echo "  make docker-down- Stop Docker Compose application"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
	python -m webbrowser "http://localhost:8000/"

test:
	pytest tests/ -v

docker-up:
	docker-compose up --build -d
	@echo "Waiting for the API to start..."
	python -c "import time; time.sleep(2)"
	python -m webbrowser "http://localhost:8000/"

docker-down:
	docker-compose down
