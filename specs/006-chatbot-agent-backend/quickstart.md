# Quickstart Guide: Chatbot Backend

**Feature**: 006-chatbot-agent-backend
**Date**: 2026-02-02
**For**: Developers implementing the chatbot backend

---

## Prerequisites

Before starting, ensure you have:

✅ **Python 3.13+** installed
✅ **UV package manager** installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
✅ **Neon PostgreSQL** database credentials (existing TODO app database)
✅ **OpenAI API key** with GPT-4o-mini access
✅ **Better Auth secret** (from existing frontend setup)
✅ **TODO Backend** running on port 9000
✅ **TODO MCP Server** running on port 3000

---

## Step 1: Project Initialization

```bash
# Navigate to repository root
cd /mnt/d/github.com/TODO-APP

# Create chatbot backend directory
mkdir chatbot-backend
cd chatbot-backend

# Initialize UV project
uv init .

# This creates:
# - pyproject.toml
# - .python-version
# - README.md
```

---

## Step 2: Install Dependencies

```bash
# Core framework
uv add fastapi
uv add "uvicorn[standard]"

# OpenAI integrations
uv add openai-agents
uv add openai-chatkit

# Authentication & Security
uv add "python-jose[cryptography]"
uv add python-dotenv

# Database
uv add asyncpg
uv add sqlmodel
uv add alembic

# HTTP client (if not included in openai-agents)
uv add httpx

# Development/Testing
uv add pytest
uv add pytest-asyncio
uv add --dev ruff
uv add --dev mypy
```

**Expected pyproject.toml**:

```toml
[project]
name = "chatbot-backend"
version = "0.1.0"
description = "AI chatbot backend with OpenAI Agents and ChatKit"
readme = "README.md"
requires-python = ">=3.13"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "openai-agents>=0.2.0",
    "openai-chatkit>=0.1.0",
    "python-jose[cryptography]>=3.3.0",
    "python-dotenv>=1.0.0",
    "asyncpg>=0.29.0",
    "sqlmodel>=0.0.16",
    "alembic>=1.13.0",
    "httpx>=0.27.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]
```

---

## Step 3: Environment Configuration

Create `.env` file in `chatbot-backend/` directory:

```bash
# Copy example
cp .env.example .env

# Edit with your actual values
nano .env
```

**.env file**:

```bash
# Database (from existing TODO app)
DATABASE_URL=postgresql+asyncpg://username:password@aws-0-us-east-1.pooler.neon.tech/neondb

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Authentication (from existing Better Auth setup)
BETTER_AUTH_SECRET=your-better-auth-secret-here

# MCP Server
MCP_SERVER_URL=http://localhost:3000/mcp

# Server settings
PORT=8001
HOST=0.0.0.0

# Timeouts (seconds)
OPENAI_TIMEOUT=30
MCP_TIMEOUT=10
```

**Security**: Never commit `.env` to git! Add to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

---

## Step 4: Create Project Structure

```bash
# Create directory structure
mkdir -p app/auth
mkdir -p app/models
mkdir -p app/store
mkdir -p app/server
mkdir -p app/utils
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/fixtures
mkdir -p alembic/versions

# Create __init__.py files
touch app/__init__.py
touch app/auth/__init__.py
touch app/models/__init__.py
touch app/store/__init__.py
touch app/server/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/fixtures/__init__.py
```

**Result**:

```
chatbot-backend/
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── main.py              # (create in Step 5)
│   ├── config.py            # (create in Step 5)
│   ├── auth/
│   ├── models/
│   ├── store/
│   ├── server/
│   └── utils/
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── alembic/
    ├── env.py
    ├── alembic.ini
    └── versions/
```

---

## Step 5: Implement Core Components

### 5.1 Configuration (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Required
    database_url: str = Field(..., env="DATABASE_URL")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    better_auth_secret: str = Field(..., env="BETTER_AUTH_SECRET")

    # Optional with defaults
    mcp_server_url: str = Field(default="http://localhost:3000/mcp", env="MCP_SERVER_URL")
    port: int = Field(default=8001, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    openai_timeout: int = Field(default=30, env="OPENAI_TIMEOUT")
    mcp_timeout: int = Field(default=10, env="MCP_TIMEOUT")

    model_config = {"env_file": ".env"}

settings = Settings()
```

### 5.2 Request Context (`app/models/request_context.py`)

```python
from dataclasses import dataclass
from fastapi import Request

@dataclass
class RequestContext:
    user_id: str
    token: str
    request: Request
```

### 5.3 JWT Verification (`app/auth/jwt.py`)

```python
from jose import jwt, JWTError
from fastapi import Header, HTTPException
from typing import Annotated
from app.config import settings

def verify_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = authorization.removeprefix("Bearer ")

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
```

### 5.4 FastAPI App (`app/main.py`)

```python
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from chatkit.server import StreamingResult
from contextlib import asynccontextmanager
from typing import Annotated
import logging

from app.config import settings
from app.auth.jwt import verify_token
from app.models.request_context import RequestContext
from app.store.neon_store import NeonPostgresStore
from app.server.chatkit_server import ChatbotServer

logger = logging.getLogger(__name__)

# Initialize ChatKit server (global, shared across requests)
store = NeonPostgresStore(settings.database_url)
chatkit_server = ChatbotServer(store=store)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting chatbot backend")
    logger.info(f"MCP Server: {settings.mcp_server_url}")
    yield
    logger.info("Shutting down chatbot backend")

app = FastAPI(
    title="Chatbot Backend",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.post("/api/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: Annotated[str, Depends(verify_token)]
):
    context = RequestContext(
        user_id=user_id,
        token=request.headers["authorization"],
        request=request
    )

    result = await chatkit_server.process(await request.body(), context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## Step 6: Database Migration

### 6.1 Initialize Alembic

```bash
# Initialize Alembic
uv run alembic init alembic

# Configure alembic.ini
nano alembic.ini
```

**Update `alembic.ini`**:

```ini
# Line ~60: Set SQLAlchemy URL to use from config
sqlalchemy.url =
# Leave blank, will use env.py to load from settings
```

### 6.2 Configure env.py

Edit `alembic/env.py`:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
from app.models.chat_thread import ChatThread
from app.models.chat_message import ChatMessage

# Alembic Config object
config = context.config

# Set SQLAlchemy URL from settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Import all SQLModel models for autogenerate
target_metadata = ChatThread.metadata

# ... rest of env.py (generated by alembic init)
```

### 6.3 Create Migration

```bash
# Generate migration from models
uv run alembic revision --autogenerate -m "Create chat_threads and chat_messages tables"

# Review generated migration in alembic/versions/
ls alembic/versions/

# Apply migration
uv run alembic upgrade head
```

---

## Step 7: Run the Server

### Development Mode (with auto-reload)

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Expected output**:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

---

## Step 8: Test the Endpoint

### Test 1: Health Check

```bash
curl http://localhost:8001/health
```

**Expected**: `{"status":"healthy"}`

### Test 2: Authentication (should fail without token)

```bash
curl -X POST http://localhost:8001/api/chatkit \
  -H "Content-Type: application/json" \
  -d '{"type":"create_thread","data":{}}'
```

**Expected**: `401 Unauthorized`

### Test 3: Get Valid JWT Token

```bash
# Login via TODO backend to get token
curl -X POST http://localhost:9000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword"}'
```

**Response**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {"id": "user_abc123", "email": "user@example.com"}
}
```

### Test 4: Create Thread (with token)

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8001/api/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "create_thread",
    "data": {"title": "Test Conversation"}
  }'
```

**Expected**:

```json
{
  "type": "thread_created",
  "data": {
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-02-02T10:00:00Z"
  }
}
```

### Test 5: Send Message (streaming)

```bash
curl -X POST http://localhost:8001/api/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  --no-buffer \
  -d '{
    "type": "send_message",
    "data": {
      "thread_id": "550e8400-e29b-41d4-a716-446655440000",
      "message": {"role": "user", "content": "Hello!"},
      "stream": true
    }
  }'
```

**Expected**: SSE stream with assistant response

---

## Step 9: Verify Integration

### Checklist

- [ ] Backend starts without errors on port 8001
- [ ] Health endpoint returns 200 OK
- [ ] Unauthenticated requests return 401
- [ ] Valid JWT tokens are accepted
- [ ] Threads can be created
- [ ] Messages can be sent and streamed
- [ ] Agent can call MCP tools (test with "Show me my tasks")
- [ ] Database tables created (chat_threads, chat_messages)
- [ ] Logs show request IDs and user IDs

### Database Verification

```bash
# Connect to database
psql $DATABASE_URL

# Check tables
\dt chat*

# View threads
SELECT id, user_id, title, created_at FROM chat_threads LIMIT 5;

# View messages
SELECT id, thread_id, role, LEFT(content, 50) as content, created_at
FROM chat_messages
ORDER BY created_at DESC
LIMIT 10;
```

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure UV virtual environment is activated:

```bash
uv sync
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
```

### Issue: Database connection fails

**Solution**: Check DATABASE_URL format:

```bash
# Correct format
DATABASE_URL=postgresql+asyncpg://username:password@host/database

# Note: +asyncpg driver for async operations
```

### Issue: MCP tools not working

**Solution**: Verify MCP server is running:

```bash
# Check MCP server health
curl http://localhost:3000/mcp
```

### Issue: JWT verification fails

**Solution**: Verify BETTER_AUTH_SECRET matches frontend:

```bash
# Get secret from frontend .env
cat ../frontend/.env | grep BETTER_AUTH_SECRET
```

---

## Next Steps

After quickstart setup:

1. **Implement remaining Store methods** (see [plan.md Decision 2](./plan.md#decision-2-neonpostgresstore-implementation-strategy))
2. **Add comprehensive tests** (see `tests/` directory structure)
3. **Implement error handling** (see [plan.md Decision 7](./plan.md#decision-7-error-handling-strategy))
4. **Configure logging** (structured logs with request IDs)
5. **Add monitoring** (health checks, metrics)

---

## References

- **Specification**: [spec.md](./spec.md)
- **Architecture Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contract**: [contracts/chatkit-endpoint.md](./contracts/chatkit-endpoint.md)
- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/
- **ChatKit Python**: https://openai.github.io/chatkit-python/
