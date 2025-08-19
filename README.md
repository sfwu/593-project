# Academic Information Management System

A **Hello World** project for software development and testing course, focusing on academic information management with structured architecture.

## Tech Stack

- **Language**: Python 3.12
- **Frontend**: Streamlit (port 9200)
- **Backend**: FastAPI (port 9100) 
- **Database**: SQLite
- **Testing**: pytest (Unit + Integration)

## Project Structure

```
593-project/
├── backend/                 # FastAPI backend (layered architecture)
│   ├── config/             # Database and settings
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic
│   ├── controllers/        # API endpoints
│   └── main.py             # FastAPI app
├── frontend/app.py         # Streamlit UI
├── tests/
│   ├── unit/               # Fast, isolated tests
│   └── integration/        # Full stack tests
├── data/                   # Database files
└── *.sh                    # Service management scripts
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start services (non-blocking)
./start.sh

# Check status
./status.sh

# Stop services
./stop.sh
```

**URLs:**
- Frontend: http://localhost:9200
- Backend API: http://localhost:9100
- API Docs: http://localhost:9100/docs

## Current Status

### ✅ Working
- FastAPI health endpoints (`/` and `/health`)
- Streamlit UI with navigation
- Service management scripts
- Testing framework structure

### ⚠️ Needs Implementation
- Student CRUD endpoints
- Database operations
- Sample data initialization

**Note**: Backend has professional layered architecture ready for implementation. See `backend/README.md` for detailed guidance.

## Testing

```bash
# Run all tests
python run_tests.py

# Run specific types
python run_tests.py --type unit
python run_tests.py --type integration
```

## Implementation Guide

1. **Models** → `backend/models/student.py`
2. **Schemas** → `backend/schemas/student_schemas.py`
3. **Repository** → `backend/repositories/student_repository.py`
4. **Service** → `backend/services/student_service.py`
5. **Controller** → `backend/controllers/student_controller.py`
6. **Wire up** → `backend/main.py`

See `backend/README.md` for detailed architecture documentation.

## For Testing Course

This project demonstrates:
- **Unit vs Integration testing** patterns
- **Layered architecture** for easy testing
- **Mock vs real database** approaches
- **Professional testing organization**

Perfect for learning software testing methodologies! 🎓