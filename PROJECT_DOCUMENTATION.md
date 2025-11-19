# ECE1779 - Inventory Management System (IMS)

## Project Overview

The Inventory Management System (IMS) is a full-stack web application designed for efficient inventory tracking and management. The system enables users to manage inventory items, track stock movements through transactions, and receive real-time notifications about inventory changes. The application supports role-based access control with two user types: **Managers** and **Staff**, each with different permissions.

### Key Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (RBAC)
- **Inventory Management**: Create, read, update, and delete inventory items with SKU tracking
- **Transaction Tracking**: Log stock in/out transactions with automatic stock validation
- **Real-Time Updates**: WebSocket integration for live updates across all connected clients
- **Low Stock Alerts**: Automatic notifications when items fall below set thresholds
- **Email Notifications**: Serverless email function integration for alert distribution
- **User Management**: Manage staff and manager accounts with role assignment

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                             │
│              http://localhost:3000                                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Components: Login, Dashboard, Items, Users, Transactions      │ │
│  │  State Management: Zustand (authStore)                         │ │
│  │  WebSocket: Real-time message listener                         │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────────────┘
                   │ HTTP/WebSocket
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND API (FastAPI)                          │
│                  http://localhost:8000                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Routers:                                                       │ │
│  │  - auth (login, register)                                       │ │
│  │  - inventory (CRUD items)                                       │ │
│  │  - transactions (stock movements)                               │ │
│  │  - users (user management)                                      │ │
│  │  - ws (WebSocket endpoint)                                      │ │
│  │                                                                 │ │
│  │  Services:                                                      │ │
│  │  - transaction_service (stock logic)                            │ │
│  │  - websocket_manager (broadcast)                                │ │
│  │  - inventory_service (stock adjustments)                        │ │
│  │  - notifications (alert system)                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────┬─────────────────────────────────┬────────────────┘
                   │ SQL                             │ HTTP Request
                   ▼                                 ▼
        ┌──────────────────┐          ┌─────────────────────────────┐
        │  PostgreSQL DB   │          │ Serverless Email Function   │
        │  :5432           │          │ (Fly.io)                    │
        │                  │          │                             │
        │ - users          │          │ SendGrid Integration        │
        │ - items          │          │ Low stock alerts            │
        │ - transactions   │          └─────────────────────────────┘
        └──────────────────┘
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | React | 18.2.0 |
| **Backend** | FastAPI | Latest |
| **Database** | PostgreSQL | Latest |
| **Authentication** | JWT + bcrypt | JWT, python-jose |
| **State Management** | Zustand | 4.4.1 |
| **API Client** | Axios | 1.5.0 |
| **Real-time** | WebSocket | Native (Python/JS) |
| **Email** | SendGrid | @sendgrid/mail 7.7.0 |
| **Containerization** | Docker | Docker Compose |
| **Web Server** | Uvicorn | standard |

---

## Folder Structure & File Organization

### Root Level

```
ece1779/
├── docker-compose.yml          # Multi-container orchestration
├── PROJECT_DOCUMENTATION.md    # This file
├── app/                        # FastAPI backend application
├── frontend/                   # React frontend application
├── infra/                      # Infrastructure files (DB init)
├── serverless-email/           # Serverless email service
└── tests/                      # Unit tests
```

---

## Detailed File Structure

### Backend Application (`app/`)

```
app/
├── main.py                     # FastAPI app initialization, CORS config, router registration
├── database.py                 # SQLAlchemy engine, session, base model setup
├── models.py                   # Legacy inventory model (deprecated)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container image for backend
├── fly.toml                    # Fly.io deployment config
├── __init__.py
│
├── core/                       # Core application configuration
│   ├── config.py              # Settings management (Pydantic)
│   ├── security.py            # Password hashing, JWT token generation
│   └── __pycache__/
│
├── db/                        # Database initialization
│   ├── database.py            # DB connection utilities (duplicate of root database.py)
│   ├── init_db.py             # Initialize DB schema & create admin user
│   └── __pycache__/
│
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py               # User model (manager/staff roles)
│   ├── item.py               # Item model (inventory items)
│   ├── transaction.py         # Transaction model (stock movements)
│   └── __pycache__/
│
├── routers/                   # API endpoint handlers
│   ├── __init__.py
│   ├── auth.py               # /auth endpoints (login, register)
│   ├── users.py              # /users endpoints (CRUD users - manager only)
│   ├── inventory.py          # /items endpoints (CRUD items, WebSocket broadcast)
│   ├── transactions.py        # /transactions endpoints (create transaction, broadcast)
│   ├── ws.py                 # /ws WebSocket endpoint
│   ├── dependencies.py        # Auth dependencies (JWT verification)
│   └── __pycache__/
│
├── schemas/                   # Pydantic data validation schemas
│   ├── __init__.py
│   ├── user.py               # UserCreate, UserOut, Token schemas
│   ├── item.py               # ItemCreate, ItemUpdate, ItemRead schemas
│   ├── transaction.py         # TransactionCreate, TransactionOut schemas
│   └── __pycache__/
│
├── services/                  # Business logic & utilities
│   ├── inventory_service.py   # Stock adjustment logic
│   ├── transaction_service.py # Stock change application & validation
│   ├── websocket_manager.py   # ConnectionManager for broadcasts
│   ├── notifications.py       # Stub for notification system
│   └── __pycache__/
│
└── __pycache__/
```

### Frontend Application (`frontend/`)

```
frontend/
├── package.json               # NPM dependencies & scripts
├── Dockerfile                 # Multi-stage build for production
├── fly.toml                   # Fly.io deployment config
├── public/
│   └── index.html            # HTML template
│
└── src/
    ├── App.js                # Main app component with routing
    ├── index.js              # React entry point
    │
    ├── api/                  # API integration layer
    │   ├── client.js         # Axios instance with auth interceptors
    │   ├── auth.js           # Auth API calls
    │   ├── items.js          # Item management API calls
    │   ├── transactions.js    # Transaction API calls
    │   └── users.js          # User management API calls
    │
    ├── components/           # Reusable React components
    │   └── Navbar.js         # Navigation bar component
    │
    ├── context/              # React Context for state
    │   ├── AuthContext.js    # Auth context provider
    │   └── Auth.css          # Auth context styling
    │
    ├── hooks/                # Custom React hooks
    │   └── useWebSocket.js   # WebSocket connection management
    │
    ├── pages/                # Page components (route handlers)
    │   ├── Login.js          # Login page
    │   ├── Register.js       # User registration page
    │   ├── Dashboard.js      # Main dashboard/home page
    │   ├── Users.js          # User management page
    │   ├── Items.js          # Item management page
    │   └── Transactions.js   # Transaction history page
    │
    ├── store/                # State management (Zustand)
    │   └── authStore.js      # Authentication state store with persistence
    │
    └── styles/               # CSS styling
        ├── App.css           # Main app styles
        └── Navbar.css        # Navbar styles
```

### Infrastructure (`infra/`)

```
infra/
└── db/
    ├── Dockerfile           # PostgreSQL container setup
    └── init/
        └── 001_schema.sql   # Database schema initialization script
```

### Serverless Email Service (`serverless-email/`)

```
serverless-email/
├── app.js                  # Express server for email function
├── package.json            # Node.js dependencies
├── Dockerfile              # Container for email service
├── fly.toml                # Fly.io deployment config
└── ReadMe.md               # Email service documentation
```

### Tests (`tests/`)

```
tests/
└── unit/
    ├── test_inventory.py   # Unit tests for inventory endpoints
    └── test_transactions.py # Unit tests for transaction logic
```

---

## Data Models & Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  full_name VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  role VARCHAR(20) NOT NULL DEFAULT 'staff' CHECK (role IN ('manager','staff')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**User Roles:**
- `manager`: Full administrative access (create/manage users, manage items)
- `staff`: Regular user access (create transactions, view items)

### Items Table
```sql
CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  sku VARCHAR(100) UNIQUE NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 0,
  low_stock_threshold INTEGER NOT NULL DEFAULT 5,
  price FLOAT NOT NULL DEFAULT 0.0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  quantity INTEGER NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('IN', 'OUT')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API Endpoints

### Authentication Routes (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| POST | `/auth/register` | Self-signup (creates staff user) | No |
| POST | `/auth/login` | Login with username/password | No |

**Request/Response Examples:**
```json
// POST /auth/register
{
  "username": "john_doe",
  "password": "securepass123"
}

// POST /auth/login
{
  "username": "john_doe",
  "password": "securepass123"
}
// Returns: { "access_token": "...", "token_type": "bearer" }
```

### Items Routes (`/items`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|----------------|------|
| GET | `/items/` | List all items | Yes | staff/manager |
| POST | `/items/` | Create new item | Yes | staff/manager |
| GET | `/items/{item_id}` | Get item details | Yes | staff/manager |
| PUT | `/items/{item_id}` | Update item | Yes | staff/manager |
| DELETE | `/items/{item_id}` | Delete item | Yes | staff/manager |

### Transactions Routes (`/transactions`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|----------------|------|
| GET | `/transactions/` | List all transactions | Yes | Any |
| POST | `/transactions/` | Create transaction (in/out) | Yes | Any |

### Users Routes (`/users`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|----------------|------|
| GET | `/users/` | List all users | Yes | manager |
| POST | `/users/` | Create user | Yes | manager |

### WebSocket Routes

| Endpoint | Description |
|----------|-------------|
| `/ws` | WebSocket connection for real-time updates |

**WebSocket Message Format:**
```json
{
  "type": "item_created|item_updated|item_deleted|transaction_created|low_stock_alert",
  "data": { /* relevant data */ }
}
```

---

## Business Logic & Workflows

### Authentication Flow

1. **Registration**
   - User submits username and password
   - Password is hashed using bcrypt
   - New user created with `staff` role by default
   - User can now login

2. **Login**
   - Username and password validated
   - JWT token generated with user ID and role
   - Token stored in client localStorage
   - Token sent in Authorization header for subsequent requests

3. **Token Verification**
   - All authenticated endpoints verify JWT token
   - Token payload contains user ID and role
   - Expired/invalid tokens return 401 Unauthorized
   - Failed auth redirects to login page

### Transaction Processing

1. **Stock In Transaction**
   - User submits transaction with item_id, quantity, type="in"
   - Item quantity increased
   - Transaction record created
   - WebSocket broadcast to all clients
   - Item updated event sent

2. **Stock Out Transaction**
   - User submits transaction with item_id, quantity, type="out"
   - System validates sufficient stock exists
   - If insufficient: return 400 error with message
   - If sufficient: decrease item quantity
   - Transaction record created
   - WebSocket broadcast to all clients

3. **Low Stock Alert**
   - After any transaction, check if quantity ≤ low_stock_threshold
   - If low stock triggered:
     - Broadcast low_stock_alert event via WebSocket
     - Send HTTP request to serverless email function
     - Email notification sent via SendGrid

### Real-Time Updates (WebSocket)

1. **Client Connection**
   - Frontend connects to `/ws` endpoint on app startup
   - Global WebSocket instance maintained
   - Auto-reconnect after 3 seconds if connection lost

2. **Broadcasting**
   - Backend broadcasts events to all connected clients
   - Events: item_created, item_updated, item_deleted, transaction_created, low_stock_alert
   - All components receive updates through `useWebSocket` hook

---

## Key Features Implementation

### 1. Role-Based Access Control (RBAC)

**Implementation:** `app/routers/dependencies.py`

```python
def get_current_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.manager:
        raise HTTPException(status_code=403, detail="Managers only")
    return current_user
```

- Manager-only endpoints: user creation, item management
- Staff/Manager endpoints: transactions, item viewing
- Public endpoints: login, register

### 2. JWT Authentication

**Implementation:** `app/core/security.py`

- Algorithm: HS256
- Token expiration: 60 minutes
- Secret key stored in environment variable
- Token contains: user_id, role, expiration

### 3. WebSocket Broadcasting

**Implementation:** `app/services/websocket_manager.py`

- Maintains set of active WebSocket connections
- `broadcast()` method sends message to all connected clients
- Automatic cleanup of disconnected clients
- Console logging for debugging

### 4. Low Stock Management

**Implementation:** `app/services/transaction_service.py`

- Configurable threshold per item
- Automatic detection after stock changes
- Integrates with email notification system
- WebSocket alert broadcast

### 5. Email Notifications

**Implementation:** `app/routers/transactions.py` + `serverless-email/app.js`

- Triggered on low stock alerts
- Calls serverless function via HTTP
- SendGrid integration for email delivery
- API key authentication for email endpoint

---

## Configuration & Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/ims_db
POSTGRES_DB=ims_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Authentication
SECRET_KEY=your-secret-key-change-in-production

# Admin User (created on startup)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Email Service
SERVERLESS_EMAIL_URL=https://your-serverless-function-url.fly.dev/send-email
EMAIL_API_KEY=your-api-key
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000
```

### Email Service (.env)

```env
SENDGRID_API_KEY=your-sendgrid-api-key
TO_EMAIL=alerts@example.com
SENDER_EMAIL=noreply@example.com
API_KEY=your-email-function-api-key
PORT=3000
```

---

## Docker Deployment

### Docker Compose Structure

The `docker-compose.yml` orchestrates three services:

1. **Database (PostgreSQL)**
   - Port: 5432
   - Volume: persistent data storage
   - Healthcheck: pg_isready verification
   - Network: app-network

2. **API (FastAPI)**
   - Port: 8000 → 8080
   - Depends on: database (healthy)
   - Volume: hot-reload during development
   - Network: app-network

3. **Frontend (React)**
   - Port: 3000
   - Depends on: API
   - Built with Vite/React Scripts
   - Network: app-network

### Running with Docker Compose

```bash
# Create .env file with required variables
# Copy the configuration from Configuration & Environment Variables section above

# Start all services
docker-compose up --build

# Access applications
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Security Considerations

### Password Security
- Passwords hashed with bcrypt (salt rounds: 12)
- Never stored in plain text
- Verified during login using bcrypt comparison

### JWT Tokens
- Signed with server secret key
- Contains user ID and role
- 60-minute expiration
- Sent as Bearer token in Authorization header

### API Authentication
- All protected routes require valid JWT
- OAuth2PasswordBearer scheme implementation
- Invalid/expired tokens return 401 Unauthorized

### CORS Configuration
- Allowed origins: http://localhost:3000, http://localhost:8000
- Credentials allowed for cross-origin requests
- All HTTP methods and headers allowed

### Email Service Authentication
- API key sent in Authorization header (Bearer token)
- Server validates API key for all requests
- Returns 401/500 on authentication failure

---

## Testing

### Unit Tests

**Inventory Tests** (`tests/unit/test_inventory.py`)
- SQLite in-memory database for testing
- Creates test manager user
- Tests item creation with JWT authentication
- Validates response structure and status codes

**Transaction Tests** (`tests/unit/test_transactions.py`)
- Tests stock in operations
- Tests stock out validation
- Tests insufficient stock error handling
- Validates low stock threshold detection

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_inventory.py -v

# Run with coverage
pytest --cov=app tests/
```

---

## Development Workflow

### Local Development Setup

```bash
# 1. Create Python virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 2. Install Python dependencies
cd app
pip install -r requirements.txt

# 3. Set up environment variables
# Create .env file in root directory with configuration from above

# 4. Initialize database
python -m app.db.init_db

# 5. Run FastAPI server
uvicorn app.main:app --reload

# 6. In another terminal, set up frontend
cd frontend
npm install
npm start

# 7. Access applications
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs (Swagger UI)
```

### Development Best Practices

1. **Code Organization**
   - Models in `models/` directory
   - API routes in `routers/` directory
   - Business logic in `services/` directory
   - Data validation in `schemas/` directory

2. **Adding New Endpoints**
   - Create route handler in `routers/`
   - Define Pydantic schemas for validation
   - Add dependency injection for auth
   - Include WebSocket broadcast where relevant
   - Write unit tests

3. **Adding New Models**
   - Create SQLAlchemy ORM model in `models/`
   - Add schema definitions in `schemas/`
   - Create migration if changing schema
   - Update `init_db.py` if needed

---

## Deployment

### Fly.io Deployment

The project includes Fly.io configuration files (`fly.toml`) for each service:

1. **API Service** (`app/fly.toml`)
2. **Frontend Service** (`frontend/fly.toml`)
3. **Email Service** (`serverless-email/fly.toml`)

Each service can be independently deployed to Fly.io with:

```bash
flyctl deploy
```

### Production Considerations

1. **Environment Variables**
   - Change `SECRET_KEY` in production
   - Use strong database passwords
   - Store API keys securely
   - Use production-grade email service

2. **Database**
   - Use managed PostgreSQL service
   - Enable automated backups
   - Configure read replicas for scaling

3. **SSL/TLS**
   - Enable HTTPS in production
   - Use valid SSL certificates
   - Enforce HSTS headers

4. **Monitoring**
   - Set up application logging
   - Monitor database performance
   - Track WebSocket connections
   - Alert on errors and failures

---

## Future Enhancements

1. **Advanced Inventory Management**
   - Batch operations for items
   - Inventory forecasting
   - Multi-location support
   - Supplier integration

2. **Analytics & Reporting**
   - Inventory turnover reports
   - Stock level analytics
   - Transaction history with filters
   - Dashboard metrics

3. **User Experience**
   - Mobile app support
   - Bulk import/export
   - Advanced search and filtering
   - Custom dashboards

4. **Integration**
   - Barcode/QR code scanning
   - Third-party API integrations
   - Payment gateway integration
   - ERP system connectivity

5. **Security**
   - Two-factor authentication (2FA)
   - Audit logging for compliance
   - Data encryption at rest
   - Rate limiting and DDoS protection

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Database connection error | DB not running | Ensure PostgreSQL container is healthy |
| WebSocket connection fails | CORS issue | Check CORS settings in main.py |
| Token validation error | Expired token | Clear localStorage, login again |
| Email not sending | SendGrid key invalid | Verify API key in environment variables |
| Frontend can't reach API | Network isolation | Ensure all services on same Docker network |

### Debug Logging

- Backend: Check container logs with `docker-compose logs api`
- Frontend: Check browser console for errors
- Database: Check PostgreSQL logs in container

---

## Contact & Support

For questions or issues, please refer to the project repository or contact the development team.

---

## Document Metadata

- **Project:** ECE1779 - Inventory Management System
- **Version:** 1.0.0
- **Last Updated:** November 2024
- **Branch:** feature/docker-swarm
- **Status:** Active Development
