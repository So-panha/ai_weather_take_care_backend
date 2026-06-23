# AI Weather Take Care Backend

Production-ready backend API built using modern Python frameworks and implementing Clean Architecture patterns.

## Tech Stack
* **Framework:** FastAPI
* **Database:** PostgreSQL with async SQLAlchemy 2.0 ORM
* **Migrations:** Alembic
* **Data Validation:** Pydantic v2
* **Authentication:** JWT, Bcrypt
* **Third Party APIs:** OpenWeatherMap, Gemini AI (Google GenAI)
* **Testing:** Pytest with HTTPX and pytest-asyncio
* **Rate Limiting:** SlowAPI (in-memory standard, extensible to Redis)
* **Containerization:** Docker & Docker Compose

## Features Overview
* Full JWT Authentication (Register, Login, Role-based constraints, Login brute-force locking).
* Complete User CRUD actions.
* Clean Architecture separation of concerns: API Routes -> Services -> Repositories -> Models.
* External API Integrations (Weather and Gemini AI Chatbot helper).
* Production-grade tooling: Structured Logging, Healthchecks, global Exception Handling.

## Running the Application

Create your `.env` file first based off of `.env.example`. Be sure to plug in your Gemini and OpenWeatherMap API keys.

### With Docker
```bash
docker-compose up --build -d
```
The FastAPI instance will boot at `http://localhost:8000`. Swagger ui at `http://localhost:8000/docs`.

### Locally (Windows/Powershell)
1. Setup virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
2. You must have PostgreSQL installed and running locally, matching your `.env` configuration.
3. Apply database migrations:
```powershell
alembic upgrade head
```
4. Start FastAPI server:
```powershell
uvicorn app.main:app --reload
```

## Running Tests
Tests are executed using `pytest` interacting with an in-memory test database structure so your data is not mutated. Setup the `venv` and run:

```bash
pytest
```
