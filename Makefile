# Makefile for project commands

.PHONY: install lint format test run

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

lint:
	@echo "Running flake8..."
	flake8 src

format:
	@echo "Formatting code with black and isort..."
	black src
	isort src

test:
	@echo "Running tests..."
	pytest

run:
	@echo "Running FastAPI app..."
	uvicorn src.main:app --reload

run-prod:
	@echo "Running FastAPI app in production..."
	gunicorn -k uvicorn.workers.UvicornWorker src.main:app
