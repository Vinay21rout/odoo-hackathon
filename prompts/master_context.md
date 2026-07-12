# EcoSphere AI - Master Context

## Project Overview

EcoSphere AI is an ESG (Environmental, Social, Governance) Management Platform developed for the Odoo Hackathon.

The objective is to build a modern ERP-like ESG platform that helps organizations monitor, manage and improve sustainability metrics.

This is a hackathon MVP, not a production SaaS.

---

# Tech Stack

Frontend

- HTML5
- CSS3
- Vanilla JavaScript

Backend

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 18
- Alembic

Authentication

- Firebase Authentication

AI

- LangChain
- LangGraph
- Gemini API

---

# Backend Architecture

Every feature must follow

Router
↓

Service
↓

Common CRUD Service (if applicable)
↓

SQLAlchemy Model
↓

PostgreSQL

Business logic must NEVER exist inside routers.

---

# Folder Structure

models/
schemas/
services/
routers/

Each contains

auth/
organization/
environmental/
social/
governance/
gamification/

---

# Database Rules

- UUID Primary Keys
- snake_case naming
- Soft Delete
- SQLAlchemy 2 style
- PostgreSQL

Every table must inherit BaseModel.

Every table contains

id

created_at

updated_at

is_active

---

# API Rules

REST APIs only.

Example

GET /departments

POST /departments

PUT /departments/{id}

DELETE /departments/{id}

Return JSON only.

---

# API Response Format

Success

{
    "success": true,
    "message": "Operation successful",
    "data": {}
}

Failure

{
    "success": false,
    "message": "Error message"
}

---

# Validation

Use Pydantic v2.

Never trust client input.

Always validate.

---

# Error Handling

Return proper HTTP status codes.

400

401

403

404

500

---

# Naming Convention

Files

department.py

employee.py

challenge.py

Models

Department

Employee

Challenge

Variables

snake_case

Classes

PascalCase

---

# Development Rules

Never duplicate CRUD logic.

Prefer reusable services.

Keep routers thin.

Keep services clean.

Follow feature-based architecture.

---

# Hackathon Rules

Simple > Complex

Working > Fancy

Complete > Half Built

Demo Ready > Perfect

---

# Coding Style

Use type hints.

Write readable code.

Keep functions short.

Document important logic.

Follow PEP8.