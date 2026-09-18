# FastAPI Layered Architecture Template

A clean, scalable, and reusable boilerplate structure for FastAPI applications.

## Folder Structure

```text
├── app/
│   ├── config/              # App settings, environment variables & database connection
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/              # SQLAlchemy database ORM models
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── user.py
│   ├── routes/              # FastAPI APIRouter endpoints
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── schemas/             # Pydantic request & response models (DTOs)
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── services/            # Pure business logic and database operations
│   │   ├── __init__.py
│   │   └── auth_service.py
│   ├── shared/              # Cross-cutting dependencies & security helpers
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── security.py
│   └── __init__.py
├── tests/                   # Pytest test cases
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_jwt.py
├── .env.example
├── .gitignore
├── main.py                  # FastAPI app entry point
└── README.md
```
