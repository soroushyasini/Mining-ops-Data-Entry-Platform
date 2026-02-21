# سامانه ورود اطلاعات معدن — Mining Ops Data Entry Platform

A production-ready, RTL Persian web platform for gold mining operations data entry.  
Replaces Excel-based workflows with a modern, Dockerized web interface that connects to the shared PostgreSQL database used by the pipeline repo.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Frontend   │    │   Backend    │    │ PostgreSQL│ │
│  │  React + Vite│◄──►│  FastAPI     │◄──►│  (shared) │ │
│  │  TailwindCSS │    │  SQLAlchemy  │    │           │ │
│  │  Port: 5173  │    │  Port: 8000  │    │ Port:5432 │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
              soroushyasini/Data-deriven-mine-ops
                   (reads same PostgreSQL DB)
```

---

## Quick Start with Docker

```bash
# 1. Clone the repo
git clone https://github.com/soroushyasini/-Mining-ops-Data-Entry-Platform.git
cd -Mining-ops-Data-Entry-Platform

# 2. Copy env file
cp .env.example .env

# 3. Start all services
docker compose up --build

# 4. Seed initial data (drivers, trucks, facilities)
curl http://localhost:8000/api/seed/

# 5. Open the app
open http://localhost:5173
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://mining_user:mining_pass@postgres:5432/mining_ops` | PostgreSQL connection string |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS allowed origin |
| `ALLOW_SEED` | `true` | Enable `/api/seed/` endpoint |

---

## API Documentation

FastAPI auto-docs are available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/drivers/` | List all drivers |
| `POST` | `/api/drivers/` | Create driver |
| `GET` | `/api/lookup/truck/{number}` | Smart auto-fill lookup |
| `GET` | `/api/bunker-loads/` | List bunker loads |
| `POST` | `/api/shipments/bulk-preview` | Preview Excel import |
| `POST` | `/api/shipments/bulk-confirm` | Confirm bulk import |
| `GET` | `/api/seed/` | Seed initial data (dev only) |

---

## Database Schema Overview

```
Facility ──< Shipment >── Driver
             Shipment >── Truck
Facility ──< BunkerLoad >── Driver
Facility ──< LabSample
Facility ──< TransportCost
Driver   ──< Payment
Alert (standalone)
```

All dates are stored as Jalali (Persian calendar) strings in `YYYY/MM/DD` format.  
`Driver` has two additional fields vs. the original pipeline schema: `bank_account` (SHABA) and `phone`.

---

## Connecting to the Existing Pipeline Repo

This platform uses the **same PostgreSQL database** as `soroushyasini/Data-deriven-mine-ops`.

To connect:
1. Set `DATABASE_URL` to point to the shared PostgreSQL instance
2. The models in `backend/app/models.py` mirror the pipeline's schema exactly (with additive-only changes to `Driver`)
3. Both services can run simultaneously against the same database

---

## Adding a New Module

The architecture is designed for easy expansion. Follow these steps:

### 1. Backend

**a. Add the model** in `backend/app/models.py`:
```python
class MyNewEntity(Base):
    __tablename__ = "my_new_entities"
    id = Column(Integer, primary_key=True, index=True)
    # ... fields
```

**b. Add the schema** in `backend/app/schemas/my_entity.py`:
```python
from pydantic import BaseModel
class MyEntityCreate(BaseModel): ...
class MyEntityUpdate(BaseModel): ...
class MyEntityRead(MyEntityCreate):
    id: int
    model_config = {"from_attributes": True}
```

**c. Add the router** in `backend/app/routers/my_entity.py`:
```python
router = APIRouter(prefix="/my-entities", tags=["my_entities"])
# ... CRUD endpoints
```

**d. Register in `backend/app/routers/__init__.py`**:
```python
from .my_entity import router as my_entity_router
```

**e. Register in `backend/app/main.py`**:
```python
app.include_router(my_entity_router, prefix="/api")
```

### 2. Frontend

**a. Add API module** in `frontend/src/api/myEntity.js`:
```js
import client from './client'
export const getMyEntities = () => client.get('/api/my-entities/').then(r => r.data)
// ... other CRUD functions
```

**b. Add form component** in `frontend/src/components/forms/MyEntityForm.jsx`

**c. Add page component** in `frontend/src/pages/MyEntities.jsx`

**d. Add route** in `frontend/src/App.jsx`:
```jsx
<Route path="my-entities" element={<MyEntities />} />
```

**e. Add sidebar entry** in `frontend/src/components/layout/Sidebar.jsx`:
```js
const NAV_ITEMS = [
  // ... existing items
  { path: '/my-entities', label: 'موجودیت جدید', icon: SomeIcon },
]
```

That's it! The new module is fully integrated with no other files needing changes.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python 3.11), SQLAlchemy ORM, Pydantic v2, Alembic |
| **Frontend** | React 18 + Vite, TailwindCSS v3, React Query v5 |
| **Language/RTL** | Full Persian (Farsi) RTL UI, Jalali calendar |
| **Database** | PostgreSQL 15 |
| **Container** | Docker + Docker Compose |
| **Forms** | React Hook Form + Zod |
| **Icons** | Lucide React |
| **Fonts** | Vazirmatn |
