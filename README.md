# FastAPI Authentication and Authorization

This is a layered FastAPI backend with JWT authentication and database-backed role-based access control (RBAC).

## Project structure

```text
app/
├── config/          # Environment settings and database connection
├── models/          # User, Role, and Permission SQLAlchemy models
├── routes/          # Authentication and authorization API routes
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic
└── shared/          # JWT dependencies, security helpers, and permission dependency
```

## Authentication flow

```text
JWT → get_current_user_jwt → authenticated user
```

Existing authentication remains responsible for registration, login, token refresh, logout, and the `/auth/me` endpoint.

## Authorization flow

```text
Authenticated user → role loaded from database → Casbin permission check → allow or HTTP 403
```

Roles and permissions are stored in the database:

- `MEMBER`: `task:read_assigned`, `task:create`, `task:update_assigned`
- `ADMIN`: all member permissions plus `task:delete`, `project:read_all`, and `user:manage`

The project currently provides role-management endpoints only. Task and project APIs should be added later in their own modules when those features exist in the backend.

## Database migration

Alembic records the schema changes needed for `Role`, `Permission`, and the user-to-role relationship.

For an existing database with the original `users` table:

```powershell
alembic stamp 0001_create_users
alembic upgrade head
```

For a new database:

```powershell
alembic upgrade head
```
