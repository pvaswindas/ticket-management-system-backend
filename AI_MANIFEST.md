# AI Context Manifest (`AI_MANIFEST.md`)

> **Repository ID**: `ticsol_backend`  
> **Project Name**: Ticket Management System Backend  
> **Framework**: Django 5.1.7 / Django REST Framework (DRF) 3.15.2  
> **Primary Language**: Python 3.11+  
> **Document Purpose**: Machine-readable architectural blueprint and context manifest for Large Language Models (LLMs) and automated agents.

---

## 1. System Architecture & Data Flow

### 1.1 Architectural Overview
`ticsol_backend` is a RESTful API web service built using Django and Django REST Framework. It provides authentication, user management, and ticket lifecycle tracking with role-based access control (RBAC).

```
                    +-------------------------------------+
                    |          HTTP Client / SPA          |
                    +-------------------------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |       Gunicorn WSGI / ASGI          |
                    +-------------------------------------+
                                       |
                                       v
                    +-------------------------------------+
                    |  ticsol.urls / Security Middleware  |
                    | (corsheaders, SimpleJWT, Security)  |
                    +-------------------------------------+
                                /             \
                               v               v
            +---------------------+   +---------------------+
            |    accounts App     |   |     tickets App     |
            | (User Auth & Mgmt)  |   |  (Ticket Lifecycle) |
            +---------------------+   +---------------------+
                                \             /
                                 v           v
                    +-------------------------------------+
                    |        PostgreSQL Database          |
                    |     (via dj-database-url / ORM)     |
                    +-------------------------------------+
```

### 1.2 Authentication & Token Flow
Authentication relies on JSON Web Tokens (JWT) using `djangorestframework_simplejwt`.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant AuthAPI as /auth/login/
    participant RefreshAPI as /auth/token/refresh/
    participant LogoutAPI as /auth/logout/
    participant DB as PostgreSQL (Token Blacklist)

    Client->>AuthAPI: POST {email, password}
    AuthAPI-->>Client: 200 OK {access_token (30m), refresh_token (1d), email, role}
    
    Note over Client,RefreshAPI: Subsequent Requests include HTTP Header: Authorization: Bearer <access_token>
    
    Client->>RefreshAPI: POST {refresh}
    RefreshAPI-->>Client: 200 OK {access_token, refresh_token (rotated)}
    
    Client->>LogoutAPI: POST {refresh}
    LogoutAPI->>DB: Blacklist refresh token
    LogoutAPI-->>Client: 200 OK {status: "success", message: "Logout successful"}
```

### 1.3 Ticket Lifecycle & Permission Flow

```mermaid
stateDiagram-v2
    [*] --> Open : Created by Regular User (is_staff=False)
    Open --> InProgress : Admin assigns ticket (assigned_to != null)
    Open --> Resolved : Status changed to resolved
    InProgress --> Resolved : Status changed to resolved
    Resolved --> [*] : Locked (Read-Only to All Users)
```

---

## 2. Core Modules & File System Structure

```
/home/aswin/code/broto/ticsol_backend/
├── manage.py                          # Django CLI entry point
├── requirements.txt                   # Dependency manifests
├── ticsol/                            # Core Configuration Directory
│   ├── __init__.py
│   ├── asgi.py                        # ASGI deployment entrypoint
│   ├── settings.py                    # Project configuration, JWT settings, DB parsing
│   ├── urls.py                        # Root URL routing
│   └── wsgi.py                        # WSGI deployment entrypoint
├── accounts/                          # User & Authentication Application
│   ├── __init__.py
│   ├── admin.py                       # CustomUserAdmin registration
│   ├── apps.py                        # Accounts app config
│   ├── models.py                      # User model & CustomUserManager
│   ├── serializers.py                 # User serializers (Login, Register, List, Status)
│   ├── urls.py                        # Auth & User API routes
│   ├── validators.py                  # Password complexity validator
│   ├── views.py                       # Auth, Logout, User stats, User status views
│   └── migrations/
│       ├── 0001_initial.py
│       └── __init__.py
└── tickets/                           # Ticket Management Application
    ├── __init__.py
    ├── admin.py                       # TicketAdmin registration
    ├── apps.py                        # Tickets app config
    ├── models.py                      # Ticket model & auto-status transition save hook
    ├── pagination.py                  # TicketPagination configuration
    ├── permissions.py                 # IsOwnerOrAdmin & CanEditTicket permissions
    ├── serializers.py                 # TicketSerializer & update validations
    ├── urls.py                        # Ticket ViewSet & Stats API routes
    ├── views.py                       # TicketViewSet, TicketStatsView, UserTicketStatsView
    └── migrations/
        ├── 0001_initial.py
        ├── 0002_delete_ticket.py
        ├── 0003_initial.py
        ├── 0004_alter_ticket_options.py
        └── __init__.py
```

---

## 3. Database Schemas & Data Models

### 3.1 `accounts.User` Model
- **File**: `accounts/models.py`
- **Table Name**: `accounts_user`
- **Description**: Custom Django user model inheriting from `AbstractUser`. Standard `username` field is removed (`username = None`). Email is unique and acts as `USERNAME_FIELD`.

```python
# Model Definition Summary
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)                  # Required, Unique, Primary Auth Identifier
    role = models.CharField(
        max_length=10,
        choices=[('user', 'User'), ('admin', 'Admin')],
        default='user'
    )
    is_active = models.BooleanField(default=True)            # Controls active/suspended status
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

#### SQL Schema Representation
```sql
CREATE TABLE accounts_user (
    id bigint NOT NULL GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    password varchar(128) NOT NULL,
    last_login timestamp with time zone NULL,
    is_superuser boolean NOT NULL DEFAULT false,
    first_name varchar(150) NOT NULL DEFAULT '',
    last_name varchar(150) NOT NULL DEFAULT '',
    is_staff boolean NOT NULL DEFAULT false,
    is_active boolean NOT NULL DEFAULT true,
    date_joined timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email varchar(254) NOT NULL UNIQUE,
    role varchar(10) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);
```

---

### 3.2 `tickets.Ticket` Model
- **File**: `tickets/models.py`
- **Table Name**: `tickets_ticket`
- **Description**: Ticket tracking entity linked to a creator (`created_user`). Includes built-in save hook for status transition logic.

```python
# Model Definition Summary
class Ticket(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='low'
    )
    status = models.CharField(
        max_length=20,
        choices=[('open', 'Open'), ('in-progress', 'In-Progress'), ('resolved', 'Resolved')],
        default='open'
    )
    created_user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_to = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.assigned_to and self.status == 'open':
            self.status = 'in-progress'
        super().save(*args, **kwargs)
```

#### SQL Schema Representation
```sql
CREATE TABLE tickets_ticket (
    id bigint NOT NULL GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    title varchar(255) NOT NULL,
    description text NOT NULL,
    priority varchar(10) NOT NULL DEFAULT 'low' CHECK (priority IN ('low', 'medium', 'high')),
    status varchar(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in-progress', 'resolved')),
    assigned_to varchar(255) NULL,
    created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_user_id bigint NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
);
CREATE INDEX tickets_ticket_created_user_id_idx ON tickets_ticket(created_user_id);
```

---

## 4. API Endpoints & Integration Surface

Base Router URL: Root includes `auth/` and `tickets/`.

### 4.1 Authentication & User Management Endpoints (`/auth/`)
- **Route File**: `accounts/urls.py`

| Endpoint Path | HTTP Method | Permission Class | Request Body / Params | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/auth/login/` | `POST` | `AllowAny` | `{ email, password }` | Authenticates user; updates `last_login`; returns access & refresh tokens, email, role. |
| `/auth/register/` | `POST` | `IsAdminUser` | `{ email, password, confirm_password, role }` | Admin-only registration of new users/admins. Enforces password strength. |
| `/auth/logout/` | `POST` | `IsAuthenticated` | `{ refresh }` | Blacklists the provided refresh token. |
| `/auth/token/refresh/` | `POST` | `AllowAny` | `{ refresh }` | DRF SimpleJWT token refresh view. Returns rotated tokens. |
| `/auth/status/` | `GET` | `IsAuthenticated` | None | Returns current user active/suspended status and role (`{ status, role }`). |
| `/auth/users/` | `GET` | `IsAdminUser` | None | Returns list of non-staff users (`is_staff=False`) ordered by `-date_joined`. |
| `/auth/users/<user_id>/status/` | `PATCH` | `IsAdminUser` | `{ is_active: boolean }` | Admin update of user status. Prevents self-deactivation. |
| `/auth/users/stats/` | `GET` | `IsAdminUser` | None | Admin metrics: `totalUsers`, `activeUsers`, `inactiveUsers`, `adminUsers`, `regularUsers`, `userGrowthByMonth`, `userActivityScore`. |

---

### 4.2 Ticket Endpoints (`/tickets/`)
- **Route File**: `tickets/urls.py`

| Endpoint Path | HTTP Method | Permission Class | Request Body / Params | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/tickets/` | `GET` | `IsAuthenticated`, `IsOwnerOrAdmin` | Query Params: `status`, `priority`, `page`, `page_size`, `search` | Lists tickets. Staff members see all tickets; regular users see only their own tickets. |
| `/tickets/` | `POST` | `IsAuthenticated`, `IsOwnerOrAdmin` | `{ title, description, priority, status }` | Creates ticket for logged-in user. **Admins forbidden (`PermissionDenied`)**. |
| `/tickets/<id>/` | `GET` | `IsAuthenticated`, `IsOwnerOrAdmin` | None | Retrieves detail of specific ticket if owner or admin. |
| `/tickets/<id>/` | `PUT`/`PATCH` | `IsAuthenticated`, `CanEditTicket` | `{ title, description, priority, status, assigned_to }` | Updates ticket. Forbidden if resolved. Non-staff cannot modify `assigned_to`. |
| `/tickets/<id>/` | `DELETE` | `IsAuthenticated`, `IsOwnerOrAdmin` | None | Deletes ticket if owner or staff member. |
| `/tickets/stats/` | `GET` | `IsAdminUser` | None | Admin dashboard statistics: status counts, priority distribution, monthly trends, recent 5 tickets. |
| `/tickets/user-stats/` | `GET` | `IsAuthenticated` | None | User dashboard metrics: `totalTickets`, `openTickets`, `inProgressTickets`, `resolvedTickets` for current user. |

---

## 5. Security & Business Logic Invariants

1. **Role Enforcement**:
   - `User.role` can be `'user'` or `'admin'`.
   - `create_superuser` automatically sets `role = 'admin'`, `is_staff = True`, `is_superuser = True`.
2. **Admin Action Boundaries**:
   - Admins **cannot create tickets** (`tickets.views.TicketViewSet.perform_create` raises `PermissionDenied`).
   - Only admins can set or edit `assigned_to` (`tickets.serializers.TicketSerializer.update`).
   - Admins cannot deactivate their own user account (`accounts.views.UserStatusView.patch`).
3. **Ticket Editing Lock**:
   - Tickets with status `'resolved'` **cannot be updated by anyone** (`tickets.permissions.CanEditTicket` returns `False`, and `TicketSerializer.update` raises `ValidationError`).
4. **Auto-Status Transition**:
   - Setting `assigned_to` on an `'open'` ticket automatically transitions status to `'in-progress'` in `Ticket.save()`.
5. **Password Complexity Rules**:
   - Minimum 8 characters.
   - At least 1 uppercase letter (`[A-Z]`).
   - At least 1 lowercase letter (`[a-z]`).
   - At least 1 digit (`\d`).
   - At least 1 special character (`[!@#$%^&*(),.?":{}|<>]`).

---

## 6. Setup & Configuration Parameters

### 6.1 Environment Variables (`.env`)
Configuration handled via `environs` in `ticsol/settings.py`:

| Variable Name | Type | Description | Example / Default |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | String | Django secret key (Required) | `django-insecure-...` |
| `DATABASE_EXTERNAL_URL` | String | PostgreSQL database connection string | `postgresql://user:pass@localhost:5432/ticsol` |
| `ALLOWED_HOSTS` | List[String] | Allowed host headers | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | List[String] | CORS origin whitelist | `http://localhost:5173,http://localhost:3000` |
| `CSRF_TRUSTED_ORIGINS` | List[String] | Trusted CSRF origins | `http://localhost:5173` |

### 6.2 Application Launch Commands
```bash
# Setup Environment
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Database Migrations
python manage.py makemigrations
python manage.py migrate

# Create Admin User
python manage.py createsuperuser

# Execution
python manage.py runserver                  # Local Development
gunicorn ticsol.wsgi:application            # Production WSGI Server
```

---

## 7. Known Legacy & Deprecated Dependencies / Code Anomalies

> [!WARNING]
> The following anomalies and technical debts exist in the repository as of the current commit. They must be documented as-is and preserved until explicit refactoring requests are made.

1. **Dual PostgreSQL Drivers in `requirements.txt`**:
   - Both `psycopg==3.2.6` (psycopg3) and `psycopg2==2.9.10` are declared simultaneously in `requirements.txt`.
2. **Unused Package Dependency**:
   - `marshmallow==3.26.1` is listed in `requirements.txt` but is never imported or utilized in any module.
3. **Invalid Search Field Reference in `tickets/admin.py`**:
   - In `tickets/admin.py`, `search_fields` includes `'created_user__username'`. However, `username` was explicitly removed from `User` (`username = None` in `accounts/models.py`). Admin search on username will fail if triggered.
4. **Redundant Parameter in Login Serializer**:
   - `LoginUserSerializer` declares `role = serializers.CharField(required=False)`, but this field is ignored during authentication validation.
5. **Hardcoded Debug Setting**:
   - `DEBUG = False` is hardcoded on line 17 of `ticsol/settings.py` rather than reading from `env.bool('DEBUG', default=False)`.
