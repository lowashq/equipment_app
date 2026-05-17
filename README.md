# University Equipment Rental Management System

Base infrastructure for a university equipment rental management platform. The stack includes PostgreSQL for persistence, Keycloak for authentication and roles, a FastAPI backend, a placeholder React frontend, and a placeholder Clojure decision engine.

## Prerequisites

- Docker
- Docker Compose

## Run The Project

```bash
cp .env.example .env
docker compose up --build
```

## Service URLs

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Keycloak Admin | http://localhost:8080 (admin/admin) |
| Decision Engine | http://localhost:3001 |

## Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```
