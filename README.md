# TicSol — Ticket Management System Backend

A RESTful web service API powered by Django and Django REST Framework for managing support tickets, user authentication, role-based access control, and administrative analytics.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | Django 5.1.7 |
| **API Engine** | Django REST Framework (DRF) 3.15.2 |
| **Authentication** | SimpleJWT 5.5.0 (JWT Access & Refresh Token Blacklisting) |
| **Database** | PostgreSQL (`psycopg` 3.2.6 & `dj-database-url` 2.3.0) |
| **Environment** | `environs` 14.1.1 & `python-dotenv` 1.0.1 |
| **WSGI Server** | Gunicorn 23.0.0 |

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- PostgreSQL database instance

### 2. Environment Setup
Clone the repository and set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key
DATABASE_EXTERNAL_URL=postgresql://username:password@localhost:5432/ticsol_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:5173
```

### 3. Database Initialization
Run migrations and create an initial administrator account:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Running the Server

#### Development Mode
```bash
python manage.py runserver
```

#### Production Mode
```bash
gunicorn ticsol.wsgi:application
```

---

## API Overview

- **Admin Console**: `/admin/`
- **Authentication Routes**: `/auth/`
  - `POST /auth/login/` - User authentication & JWT issuance
  - `POST /auth/register/` - User registration (Admin only)
  - `POST /auth/logout/` - Token revocation
  - `POST /auth/token/refresh/` - Token rotation
  - `GET /auth/status/` - User status & role query
  - `GET /auth/users/` - List users (Admin only)
  - `PATCH /auth/users/<id>/status/` - Update user active status (Admin only)
  - `GET /auth/users/stats/` - User metrics (Admin only)
- **Ticket Management Routes**: `/tickets/`
  - `GET /tickets/` - List tickets (filtered by role/owner)
  - `POST /tickets/` - Create ticket (Regular users only)
  - `GET /tickets/<id>/` - Retrieve ticket details
  - `PUT/PATCH /tickets/<id>/` - Update ticket (Forbidden if resolved)
  - `DELETE /tickets/<id>/` - Delete ticket
  - `GET /tickets/stats/` - Ticket statistics (Admin only)
  - `GET /tickets/user-stats/` - Ticket statistics (User dashboard)
