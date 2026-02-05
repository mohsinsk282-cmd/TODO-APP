# Chatbot Backend

AI chatbot backend with OpenAI Agents and ChatKit MCP Integration.

## Project Overview

This project is a FastAPI-based chatbot backend that integrates with the OpenAI Agents SDK and the ChatKit Python SDK. It provides an AI assistant capable of managing a user's todos through the existing TODO MCP Server.

### Features:
- Accepts authenticated chat messages from a Next.js frontend.
- Verifies Better Auth JWT tokens and extracts `user_id` for request scoping.
- Uses `ChatKitServer` with a custom `respond()` method to coordinate agent responses.
- Creates per-request Agent instances with the GPT-4o-mini model and user-specific instructions.
- Connects agents to the TODO MCP Server via `MCPServerStreamableHttp` with token forwarding.
- Streams agent responses token-by-token using `Runner.run_streamed()` and ChatKit's `StreamingResult`.
- Persists conversation threads and messages in a Neon PostgreSQL database.

## Architecture

### Request Flow
```
User (Frontend)
    │ POST /api/chatkit
    │ Authorization: Bearer <jwt>
    ▼
[1] JWT Verification (FastAPI Dependency)
    │ Extract user_id from 'sub' claim
    │ Validate signature with BETTER_AUTH_SECRET
    ▼
[2] RequestContext Creation
    │ {user_id, token, request}
    ▼
[3] ChatKitServer.process(body, context)
    │ Parse ChatKit protocol message
    │ Route to appropriate Store method
    ▼
[4] Custom respond() Method (for user messages)
    │ Load thread history (last 20 messages)
    │ Create Agent with user-specific instructions
    │ Create MCP client with token in headers
    ▼
[5] Runner.run_streamed(agent, input)
    │ Agent calls MCP tools (list_tasks, add_task, etc.)
    │ MCP client forwards token to MCP server
    ▼
[6] MCP Server → TODO Backend API
    │ MCP server validates token
    │ Backend enforces user_id isolation
    ▼
[7] Stream Response Events
    │ Agent output → ChatKit events
    │ SSE streaming to frontend
    ▼
[8] Persist Messages (async)
    │ Save user message and assistant response
    │ Update thread timestamps
    ▼
Frontend (ChatKit UI)
    │ Display streamed response
    │ Update conversation history
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────┐
│ chatbot-backend (Port 8001)                             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────┐ │
│  │ FastAPI      │────>│ JWT Verify   │────>│ ChatKit │ │
│  │ /api/chatkit │     │ (Dependency) │     │ Server  │ │
│  └──────────────┘     └──────────────┘     └────┬────┘ │
│                                                  │      │
│                                            ┌─────▼────┐ │
│  ┌──────────────┐                         │ respond()│ │
│  │ Neon         │<────────────────────────│  method  │ │
│  │ Postgres     │     Store methods       └────┬─────┘ │
│  │ Store        │     (load/save thread)       │       │
│  └──────────────┘                              │       │
│         │                                 ┌────▼─────┐ │
│         │ chat_threads                    │  Agent   │ │
│         │ chat_messages                   │ Factory  │ │
│         │                                 └────┬─────┘ │
│  ┌──────▼──────┐                               │       │
│  │ PostgreSQL  │                         ┌─────▼─────┐│
│  │ Database    │                         │MCP Client ││
│  └─────────────┘                         │(HTTP)     ││
│                                          └─────┬──────┘│
└───────────────────────────────────────────────┼───────┘
                                                │
                                                │ Authorization: Bearer <token>
                                                │
┌───────────────────────────────────────────────▼───────┐
│ TODO MCP Server (Port 3000)                           │
├───────────────────────────────────────────────────────┤
│  ┌────────────┐     ┌────────────┐     ┌──────────┐  │
│  │ AuthToken  │────>│ MCP Tools  │────>│  httpx   │  │
│  │ Middleware │     │ (5 tools)  │     │  Client  │  │
│  └────────────┘     └────────────┘     └────┬─────┘  │
└─────────────────────────────────────────────┼────────┘
                                              │
                                              │ Authorization: Bearer <token>
                                              │
┌─────────────────────────────────────────────▼─────────┐
│ TODO Backend API (Port 9000)                          │
├───────────────────────────────────────────────────────┤
│  ┌────────────┐     ┌────────────┐     ┌──────────┐  │
│  │ JWT Verify │────>│ Task CRUD  │────>│Database  │  │
│  │ (FastAPI)  │     │ Endpoints  │     │(Neon)    │  │
│  └────────────┘     └────────────┘     └──────────┘  │
└───────────────────────────────────────────────────────┘
```

## Quickstart

### Prerequisites

Before starting, ensure you have:

✅ **Python 3.13+** installed
✅ **UV package manager** installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
✅ **Neon PostgreSQL** database credentials (existing TODO app database)
✅ **OpenAI API key** with GPT-4o-mini access
✅ **Better Auth secret** (from existing frontend setup)
✅ **TODO Backend** running on port 9000
✅ **TODO MCP Server** running on port 3000

### Step 1: Project Initialization

```bash
# Navigate to repository root
cd /mnt/d/github.com/TODO-APP

# Create chatbot backend directory
mkdir chatbot-backend
cd chatbot-backend

# Initialize UV project
uv init .
```

### Step 2: Install Dependencies

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

### Step 3: Environment Configuration

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

### Step 4: Run the Server

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 5: Database Setup

```bash
# Run migrations
uv run alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt chat*"
```

### Step 6: Testing

**Health Check**:
```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy"}
```

**Send Message (requires valid JWT token)**:
```bash
export TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8001/api/chatkit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --no-buffer \
  -d '{
    "type": "threads.addUserMessage",
    "threadId": null,
    "input": {"content": "Show me my tasks"}
  }'
```

## Features

### 1. Conversational AI
- **Model**: OpenAI GPT-4o-mini
- **Streaming**: Real-time token-by-token responses via SSE
- **Context**: Full conversation history maintained per thread

### 2. Task Management Integration
The agent has access to these MCP tools for task management:
- `list_tasks(status)` - List user's tasks
- `add_task(title, description)` - Create new task
- `complete_task(task_id)` - Mark task as done
- `update_task(task_id, title, description)` - Update task details
- `delete_task(task_id)` - Remove task

### 3. Persistent Storage
- **Database**: Neon PostgreSQL (serverless)
- **Tables**: `chat_threads`, `chat_messages`
- **User Isolation**: All queries filtered by user_id
- **Cascade Delete**: Automatic cleanup on user/thread deletion

### 4. Security
- **Authentication**: Better Auth JWT token verification
- **User Isolation**: Database-level user_id filtering
- **Token Forwarding**: Transparent MCP authentication
- **CORS**: Configured for frontend origin

### 5. Error Handling
Custom exception hierarchy with HTTP status codes:
- `ChatbotError` (500) - Base exception
- `AgentError` (500) - Agent execution failures
- `MCPError` (502) - MCP tool/server issues
- `StorageError` (500) - Database failures

All errors return structured JSON responses with type, message, and status_code.

### 6. Structured Logging
JSON-formatted logs with timestamps, request IDs, user IDs, and log levels.

## Development

### Code Quality

**Linting**:
```bash
uv run ruff check app/
uv run ruff format app/
```

**Type Checking**:
```bash
uv run mypy --strict app/
```

### Testing
```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html
```

## Troubleshooting

### Database Connection Fails
```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql+asyncpg://user:pass@host/db
```

### MCP Tools Not Working
```bash
# Verify MCP server is running
curl http://localhost:8000/mcp

# Ensure TODO backend is running on port 9000
```

### JWT Verification Fails
```bash
# Verify BETTER_AUTH_SECRET matches frontend
cat ../frontend/.env | grep BETTER_AUTH_SECRET
```

## Project Structure

```
chatbot-backend/
├── app/
│   ├── auth/               # JWT verification
│   ├── models/             # Data models
│   ├── server/             # ChatKit server implementation
│   ├── store/              # Database persistence
│   ├── utils/              # Utilities (errors, logging)
│   ├── config.py           # Configuration management
│   └── main.py             # FastAPI application
│
├── alembic/                # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── integration/        # Integration tests
│   └── unit/               # Unit tests
│
├── .env                    # Environment variables (not in git)
├── .env.example            # Environment template
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Performance

- **Latency**: < 3s to first response token
- **Throughput**: ~50 concurrent users per worker
- **Database**: Connection pooling (2-10 connections)
- **Streaming**: Chunked SSE for real-time responses

## License

[Your License]

## Support

For issues or questions:
- **Spec**: See `specs/006-chatbot-agent-backend/spec.md`
- **Architecture**: See `specs/006-chatbot-agent-backend/plan.md`
- **Data Model**: See `specs/006-chatbot-agent-backend/data-model.md`

---

**Version**: 0.1.0
**Last Updated**: 2026-02-04
