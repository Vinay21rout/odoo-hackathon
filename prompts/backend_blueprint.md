# EcoSphere AI Backend Blueprint

## Layers

Client

↓

FastAPI Router

↓

Service

↓

SQLAlchemy ORM

↓

PostgreSQL

---

# Feature Structure

Feature

↓

Model

↓

Schema

↓

Service

↓

Router

---

# Common Service

services/common/

crud.py

response.py

pagination.py

This folder contains reusable backend logic.

Every module should reuse these services.

---

# Models

Every model extends BaseModel.

Never duplicate

id

created_at

updated_at

is_active

---

# Routers

Routers only

Receive Request

↓

Call Service

↓

Return Response

Never write SQL inside routers.

---

# Services

Contains

CRUD

Validation

Business Rules

Database Queries

---

# Schemas

Create Schema

Update Schema

Response Schema

---

# Authentication

Firebase Authentication

↓

Verify Token

↓

Access Protected API

Passwords are never stored inside PostgreSQL.

---

# Soft Delete

Never delete rows.

Always update

is_active = False

---

# Pagination

All list APIs should support

?page=

&limit=

---

# Logging

Every request should be logged.

---

# Future Modules

Organization

Environmental

Social

Governance

Gamification

Reports

AI

All modules follow the exact same architecture.