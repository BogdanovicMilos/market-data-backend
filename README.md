## Market Data BE

Market Data backend repository

## 🚀 Architecture Overview

The Market Data BE project implements a clean, modular, and layered backend architecture in `FastAPI` with `Python 3.12` for managing and serving market data.

### Layers & Key Components:

- _API Layer_ - `application/`

   - FastAPI-based REST endpoints for stock price queries and data ingestion.
   - Routers and Pydantic schemas for request/response validation.
   - Dependency injection for service and config management.


- _Domain Layer_ - `domain/`

  - Core business logic for batch processing and data ingestion.
  - Encapsulates domain-specific operations and rules.


- _Infrastructure Layer_ - `infrastructure/`
  - SQLAlchemy models and database connection utilities.
  - Repository pattern for abstracted data access.
  - Alembic migrations for schema evolution.


- _Testing_ - `tests/`
  - Pytest-based test suite with coverage reporting.
  - Organized by component for maintainability.


### Ingestion overview:

###### <font color="#b0acf7"> Stock Data CSV file ingestion via API</font>

  - The project supports data ingestion from the Twelve Data API which we can trigger through `/api/ingestion` endpoint, allowing updates of stock market data.
   We can customize an automated pipeline with the `ingestion_config.yaml` file. In it, we can define which market symbols to ingest, set the polling interval, batch time window and specify the start date.

###### <font color="#b0acf7"> Stock Data CSV file ingestion via API</font>

- We can also upload CSV test data (csv file inside `test_data` folder) by sending a _POST_ request to the `/api/stocks-data` endpoint with the file attached. Background ingestion tasks are managed asynchronously using `Celery`, ensuring scalability and non-blocking execution of batch jobs.


### Stocks Data Provider:

- The project uses the **Twelve Data API** to fetch data during the ingestion process. API integration is managed within the application and domain layers, ensuring reliable and up-to-date market data retrieval. API keys and related settings are configured via environment variables.

<hr></hr>


## 📦 Setup

### Create virtual environment:
```bash
python3 -m venv .venv
```

Activate virtual environment:
```bash
source .venv/bin/activate
```

### Create environment variables files

- Copy `example.env` to `.env` and set the variables.

- Copy `example.env.docker` to `.env.docker` and set the variables.

### Configure `settings.py` file:

For local development:
> model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
)

For docker compose:
> model_config = SettingsConfigDict(
    env_file=".env.docker",
    env_file_encoding="utf-8",
)


### Configure `pre-commit` (Optional)
Install pre-commits:
```bash
pre-commit install
```
Run pre-commits:
```bash
pre-commit run --all-files
```

## ▶️ Run development server
Install requirements:
```bash
pip3 install -r requirements.txt -r requirements.dev.txt
```


Run migrations:
```bash
alembic upgrade head
```


Run server:
```bash
uvicorn application.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## ▶️ Run using docker compose

Run docker compose:
```bash
docker compose up --build
```

## 🧪 Tests and coverage

Get the test coverage by running:
```bash
coverage run -m pytest tests/*
```
To get the report:
```bash
coverage report -m
```
or to get HTML version:
```bash
coverage html
```

## 📚 Local documentation

`http://localhost:8000/docs`


###### <font color="#b0acf7"> Valid bearer token for testing:</font>

> VALID_BEARER_TOKEN=ek8KCVd4KjW5jGWKeWbE1yzbqDXJEBU48pllsEuy5ubSlcz4EMVWHll7D329VIsl
