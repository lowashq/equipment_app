# University Equipment Rental Management System

A full-stack university equipment rental platform for managing inventory, reservations, returns, fault reports, notifications, and reports.

The system includes:

- FastAPI backend with async SQLAlchemy and Alembic migrations
- PostgreSQL 15 database
- Keycloak 24 for SSO login and registration
- React + TypeScript frontend
- Clojure decision engine microservice for reservation approval rules
- Email notifications through SMTP, with console mock mode when SMTP is not configured
- CSV and PDF rental reports

## Prerequisites

- Docker
- Docker Compose

## Run The Project

```bash
cp .env.example .env
docker compose up --build
```

If you change `.env`, recreate the affected containers so Docker Compose reloads the values:

```bash
docker compose up -d --force-recreate backend
```

## Service URLs

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs / Swagger | http://localhost:8000/docs |
| Keycloak Admin | http://localhost:8080 |
| Decision Engine | http://localhost:3001 |

Keycloak admin credentials:

```text
admin / admin
```

## Health Checks

Backend:

```bash
curl http://localhost:8000/health
```

Decision engine:

```bash
curl http://localhost:3001/health
```

Expected response:

```json
{"status":"ok"}
```

## Seed Data

After the services are running, populate the database with test users and equipment:

```bash
docker compose exec backend python seed.py
```

The seed script is idempotent, so it can be run more than once without creating duplicate users or equipment.

## Test Users

The app supports Keycloak SSO and local JWT auth. For Keycloak, imported usernames may still use the original username while the email is synced to the SAN domain.

| Role | Email | Password |
| --- | --- | --- |
| Student | student@student.san.edu.pl | student123 |
| Staff | staff@san.edu.pl | staff123 |
| Equipment manager | manager@san.edu.pl | manager123 |
| Admin | admin@san.edu.pl | admin123 |

Registration is limited to:

- `@student.san.edu.pl` -> `student`
- `@san.edu.pl` -> `staff`

Admins can update local user roles in the frontend under `Admin -> Users`.

## Authentication

Auth endpoints are available under `/auth`:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /auth/keycloak/login`
- `GET /auth/keycloak/register`
- `GET /auth/keycloak/callback?code=...`
- `GET /auth/keycloak/logout`

The frontend login page uses Keycloak buttons for login and registration. After Keycloak redirects back to `/auth/callback`, the backend exchanges the code, syncs the user, and returns a local JWT for API access.

## Roles

| Role | Capabilities |
| --- | --- |
| `student` | Browse equipment, reserve available items, report faults, view own reservations and notifications |
| `staff` | View and approve reservations |
| `equipment_manager` | Manage equipment, resolve fault reports, view reports |
| `admin` | Equipment manager permissions plus user role management |

## Core Workflows

### Reservations

Students can reserve available equipment from the frontend. Reservation requests are checked by the Clojure decision engine.

- Score `100`: reservation becomes `active`, equipment becomes `borrowed`
- Approved score below `100`: reservation becomes `pending`, equipment becomes `reserved`
- Rejected request: reservation is not created and the frontend displays the rule reasons

Staff, equipment managers, and admins can approve pending reservations.

### Returns

Users can return active or pending reservations:

- condition `good` -> equipment becomes `available`
- condition `damaged` -> equipment becomes `damaged`

### Fault Reports

Users can report a fault from an equipment detail page.

When a fault is reported:

- a fault report is saved
- equipment immediately becomes `damaged`

Managers and admins can view fault reports under `Admin -> Fault Reports`.

Resolving a fault report:

- marks open fault reports for that equipment as resolved
- changes equipment status back to `available`

If a manager manually changes damaged equipment to `available`, open fault reports for that equipment are also resolved.

## Equipment Statuses

Current equipment statuses:

- `available`
- `reserved`
- `borrowed`
- `damaged`

Allowed status changes:

- `available` -> `reserved`, `damaged`
- `reserved` -> `borrowed`, `available`, `damaged`
- `borrowed` -> `available`, `damaged`
- `damaged` -> `available`

The old `serviced` status is no longer used.

## Decision Engine

The Clojure service runs on port `3001`.

Endpoints:

- `GET /health`
- `GET /rules`
- `POST /decide`

Reservation decisions are rule-based. Students are evaluated against availability, date, overdue rental, active rental, max rental days, and equipment type rules.

Privileged roles short-circuit the rule engine:

- `staff`
- `equipment_manager`
- `admin`

These roles immediately receive:

```clojure
{:approved true :score 100 :reasons []}
```

## Notifications

Email notifications are handled in the backend notification service.

Sent emails:

- reservation confirmation after successful reservation creation
- cancellation email after pending reservation cancellation
- return reminder 2 days before the reservation end date
- overdue rental notice for active or pending reservations past their end date

Notification history is stored in the `notifications` table and visible in the frontend under `Notifications`.

SMTP settings are read from `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

When SMTP is not configured, emails are printed to backend logs in mock mode.

Run the scheduler manually:

```bash
docker compose exec -T backend python -c "import asyncio; from app.scheduler import check_upcoming_returns; asyncio.run(check_upcoming_returns())"
```

## Reports

Managers and admins can open `Admin -> Reports`.

Available reports:

- rental statistics
- equipment by status
- top rented equipment
- unresolved fault reports count
- CSV export
- PDF export

## Useful Commands

Check containers:

```bash
docker compose ps
```

Backend logs:

```bash
docker compose logs -f backend
```

Frontend rebuild after local frontend changes:

```bash
docker compose build frontend
docker compose up -d --force-recreate frontend
```

Clojure service rebuild after rules changes:

```bash
docker compose build clojure-service
docker compose up -d --force-recreate clojure-service
```

Run backend Python compile check:

```bash
docker compose exec -T backend python -m compileall app
```

Run frontend production build:

```bash
docker compose run --rm --entrypoint npm frontend run build
```
