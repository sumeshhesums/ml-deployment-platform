# ML Deployment Platform

A production-ready full-stack ML Model Deployment Platform for deploying machine learning models as REST APIs.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                  │
│              http://localhost:5173 (Development)                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ REST API (JWT Auth)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                          │
│              http://localhost:8000 (Development)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │   Routes    │  │  Services   │  │    Core (JWT, Security)  ││
│  └─────────────┘  └─────────────┘  └─────────────────────────┘│
└─────────────────────────────┬───────────────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
┌──────────────────┐                    ┌──────────────────┐
│  PostgreSQL DB   │                    │   Model Storage  │
│  (User/Models/   │                    │   (Local/S3)     │
│   Predictions)   │                    └──────────────────┘
└──────────────────┘
```

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM (async)
- **JWT** - Authentication with access/refresh tokens
- **Pydantic** - Data validation
- **Loguru** - Structured logging

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

### DevOps
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ml-deployment-platform

# Start all services
docker compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start PostgreSQL (or use Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Run the server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Environment Variables

### Backend (.env)
```env
APP_NAME=ML Deployment Platform
DEBUG=True
ENVIRONMENT=development

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mlplatform
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/mlplatform

SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login user |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

### Models
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/models/upload` | Upload a model |
| GET | `/api/v1/models` | List all models |
| GET | `/api/v1/models/{id}` | Get model details |
| PUT | `/api/v1/models/{id}` | Update model |
| DELETE | `/api/v1/models/{id}` | Delete model |
| POST | `/api/v1/models/{id}/predict` | Make prediction |
| GET | `/api/v1/models/{id}/stats` | Get model statistics |
| GET | `/api/v1/models/{id}/history` | Get prediction history |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Root endpoint |

## Project Structure

```
ml-deployment-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Config, security, JWT
│   │   ├── db/           # Database models & setup
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── tests/            # Test files
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── context/      # React contexts
│   │   ├── pages/        # Page components
│   │   └── services/     # API service
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── README.md
```

## Deployment

### Option 1: Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Your secret key
4. Build command: `cd backend && pip install -r requirements.txt`
5. Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 2: Railway

1. Create a new project on Railway
2. Add PostgreSQL plugin
3. Deploy from GitHub
4. Set environment variables in Railway dashboard

### Option 3: AWS EC2 + RDS

1. Launch EC2 instance
2. Create RDS PostgreSQL instance
3. Configure security groups
4. Set environment variables
5. Deploy using Docker or manual setup

### Option 4: GCP Cloud Run

1. Create Cloud Run service
2. Connect Cloud SQL (PostgreSQL)
3. Deploy from container registry
4. Configure environment variables

## Security Best Practices

- **Passwords**: Hashed with bcrypt
- **JWT**: Access tokens expire in 30 minutes, refresh tokens in 7 days
- **Rate Limiting**: 60 requests per minute
- **CORS**: Configured for specific origins
- **Input Validation**: Pydantic schemas
- **Logging**: Request/response logging with request IDs

## Architecture Decisions

### Backend Architecture

The backend follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── api/          # Routes - handle HTTP requests/responses
├── core/         # Cross-cutting concerns (auth, security, config)
├── db/           # Database models and connection
├── schemas/      # Pydantic models for request/response validation
├── services/     # Business logic - independent of frameworks
└── utils/        # Utilities (middleware, logging)
```

**Key Decisions:**

1. **Async SQLAlchemy**: Used async database operations for better performance under load. The `AsyncSession` allows non-blocking I/O operations.

2. **JWT with Refresh Tokens**: Access tokens (30min) provide short-lived security, while refresh tokens (7 days) allow persistent sessions without exposing the user to long-term token theft.

3. **Pydantic for Validation**: All API inputs/outputs are validated via Pydantic schemas, ensuring type safety and automatic API documentation.

4. **Service Layer**: Business logic is isolated in services (`ModelService`, `AdminService`), making the code testable and independent of FastAPI.

### Frontend Architecture

```
src/
├── components/   # Reusable UI components (Layout, ProtectedRoute)
├── context/      # React Context for global state (Auth)
├── pages/        # Page components (views)
└── services/     # API client with Axios interceptors
```

**Key Decisions:**

1. **Axios Interceptors**: Automatically attach JWT to requests and handle token refresh on 401 errors.

2. **React Context**: `AuthContext` manages user state globally, providing authentication status to all components.

3. **Protected Routes**: Route-level protection ensures unauthenticated users cannot access the dashboard.

4. **Component Structure**: Pages are separated from components for better maintainability.

### Scalability Considerations

1. **Horizontal Scaling**: The backend is stateless (JWT-based), allowing multiple instances behind a load balancer.

2. **Database Connection Pooling**: SQLAlchemy handles connection pooling automatically.

3. **Model Storage**: Currently local filesystem; can be easily swapped for AWS S3 or Azure Blob Storage.

4. **Redis**: Included for rate limiting and future caching/queuing needs.

### Security Implementation

1. **Password Hashing**: bcrypt with salt - computationally expensive to prevent brute force.

2. **CORS**: Explicitly configured origins, not wildcards in production.

3. **Rate Limiting**: Per-IP limiting to prevent DoS attacks.

4. **Request Logging**: Structured logs with request IDs for traceability without exposing sensitive data.

## Commands to Push to GitHub

```bash
# Initialize git (if new repo)
git init
git add .
git commit -m "Initial commit: Production-ready ML Deployment Platform"

# Create main branch
git branch -M main

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ml-deployment-platform.git

# Push to GitHub
git push -u origin main
```

## License

MIT License - see LICENSE file for details.
