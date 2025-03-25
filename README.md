# 🎫 Simple Ticket Management System - Backend

## 🚀 Project Overview
Django-powered backend for ticket management system.

## 💻 Tech Stack
### Core Frameworks
- Django 5.1.7
- Django REST Framework 3.15.2
- Simple JWT 5.5.0

### Database
- PostgreSQL (psycopg 3.2.6)
- SQLite (development)
- dj-database-url 2.3.0

### Authentication
- JWT Authentication
- djangorestframework_simplejwt 5.5.0

### Additional Libraries
- django-cors-headers 4.7.0
- django-filter 25.1
- environs 14.1.1 (Environment management)
- python-dotenv 1.0.1

### Deployment
- Gunicorn 23.0.0

## 🛠️ Prerequisites
- Python 3.11+
- pip
- Virtual Environment

## 🚀 Setup

### Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Dependencies
```bash
# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
1. Create `.env` file
2. Add configuration:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Running the Server
```bash
# Development
python manage.py runserver

# Production
gunicorn ticsol.wsgi:application
```

## 📂 Project Structure
```
Server/
├── accounts/
├── tickets/
├── ticsol/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

## 🌐 API Endpoints
- `/admin/`: Django Admin
- `/api/auth/`: User endpoints
- `/api/tickets/`: Ticket endpoints

## 🧪 Testing
```bash
# Run tests
python manage.py test
```

## 🚢 Deployment Considerations
- Use PostgreSQL in production
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use strong `SECRET_KEY`

## 🤝 Contributing
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📧 Contact
**Aswin Das P V**  
**Email:** pvaswindas.dev@gmail.com  
**LinkedIn:** [pvaswindas](https://www.linkedin.com/in/pvaswindas/)  