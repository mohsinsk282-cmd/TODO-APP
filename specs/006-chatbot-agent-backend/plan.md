# Implementation Plan: Chatbot Backend with OpenAI Agents and ChatKit MCP Integration

**Branch**: `006-chatbot-agent-backend` | **Date**: 2026-02-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-chatbot-agent-backend/spec.md`

**Note**: This plan documents architecture and design decisions for the chatbot backend implementation.

## Summary

Build a FastAPI-based chatbot backend (port 8001) that integrates OpenAI Agents SDK with ChatKit Python SDK to provide an AI assistant capable of managing users' todos through the existing TODO MCP Server. The backend will:

- Accept authenticated chat messages from Next.js frontend via POST /api/chatkit endpoint
- Verify Better Auth JWT tokens and extract user_id for request scoping
- Use ChatKitServer with custom respond() method to coordinate agent responses
- Create per-request Agent instances with GPT-4o-mini model and user-specific instructions
- Connect agents to TODO MCP Server (http://localhost:3000) via MCPServerStreamableHttp with token forwarding
- Stream agent responses token-by-token using Runner.run_streamed() and ChatKit's StreamingResult
- Persist conversation threads and messages in Neon PostgreSQL via custom NeonPostgresStore
- Handle thread creation, message history loading (last 20 messages), and concurrent user isolation

## Technical Context

**Language/Version**: Python 3.13+ (leveraging modern type hints with `|` union syntax, async/await patterns)

**Primary Dependencies**:
- **FastAPI**: ASGI web framework for API endpoint (`/api/chatkit`)
- **OpenAI Agents SDK** (`openai-agents`): Agent creation, MCP integration, streaming via `Runner.run_streamed()`
- **ChatKit Python SDK** (`openai-chatkit`): `ChatKitServer` base class, `Store` interface, `ThreadStreamEvent` types
- **python-jose[cryptography]**: JWT token verification with HS256 algorithm
- **asyncpg**: Async PostgreSQL driver for Neon database connectivity
- **sqlmodel**: Type-safe ORM (SQLAlchemy + Pydantic) for chat_threads and chat_messages models
- **httpx**: Async HTTP client (already used by MCP SDK for server communication)
- **python-dotenv**: Environment variable management (.env file loading)
- **uvicorn[standard]**: ASGI server with auto-reload for development

**Storage**:
- **Neon Serverless PostgreSQL** (existing database instance)
- **New Tables**: `chat_threads` (UUID primary key, user_id FK, title, timestamps), `chat_messages` (BIGSERIAL PK, thread_id FK, role CHECK constraint, content, timestamp)
- **Indexes**: user_id (chat_threads), thread_id + created_at (chat_messages)
- **Constraints**: CASCADE DELETE for user → threads → messages cleanup

**Testing**:
- **pytest** with **pytest-asyncio** for async test functions
- **Unit tests**: JWT validation, context creation, store methods
- **Integration tests**: Full flow with test database (transactional rollbacks)
- **Contract tests**: MCP server connectivity, agent tool calls

**Target Platform**: Linux server (development: WSL2, production: serverless/container)

**Project Type**: Web backend (standalone FastAPI service, separate from existing TODO backend on port 9000)

**Performance Goals**:
- First token streamed within **3 seconds** of user message (SC-001)
- Visible content within **1 second** of agent starting generation (SC-006)
- Support **10 concurrent users** without degradation (SC-005)
- Threads with **100+ messages** without performance issues (SC-009)

**Constraints**:
- **Port 8001** (avoid conflict with TODO backend :9000, frontend :3000, MCP server :3000)
- **Stateless design**: No shared in-memory state between requests (enables horizontal scaling)
- **Token security**: Never expose JWT in agent instructions or logs (headers-only transmission)
- **No MCP server modifications**: Must work with existing TODO MCP Server as-is
- **Backward compatibility**: Must not break existing TODO app or frontend

**Scale/Scope**:
- **Multi-user**: User data isolation via user_id filtering (0% cross-access per SC-003)
- **Conversation persistence**: 100% message retrieval across sessions (SC-004)
- **Natural language accuracy**: 90%+ task interpretation (SC-010)
- **Error coverage**: Meaningful error messages for 100% of failure scenarios (SC-008)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. SDD-RI Methodology
- **Status**: PASS
- **Evidence**: Following prescribed workflow: `/sp.specify` → `/sp.plan` (current) → `/sp.tasks` → `/sp.implement`
- **Traceability**: All implementation will map to 41 functional requirements (FR-001 to FR-041) in spec.md

### ✅ II. Pythonic Excellence
- **Status**: PASS
- **Evidence**: Python 3.13+ with modern features (type unions `|`, async/await), PEP 8 adherence planned
- **Quality Tools**: mypy --strict (type checking), ruff check (linting), ruff format (formatting)

### ✅ III. Persistent Relational State
- **Status**: PASS
- **Evidence**:
  - Using existing Neon PostgreSQL database (same instance as TODO app)
  - New tables: chat_threads (user_id FK), chat_messages (thread_id FK)
  - User isolation: All queries filter by authenticated user_id (FR-004, SC-003)
  - SQLModel for type-safe ORM operations
  - CASCADE DELETE constraints for data consistency

### ✅ IV. Type Safety & Documentation
- **Status**: PASS (will enforce during implementation)
- **Evidence**:
  - Complete type hints for all functions (parameters, return values)
  - Google-style docstrings for all public methods
  - Pydantic models for request/response validation (FastAPI integration)

### ✅ V. Terminal-Based Verification
- **Status**: PASS
- **Evidence**:
  - REST API testable via curl/httpx
  - Structured JSON responses with proper HTTP status codes (200, 401, 404, 500)
  - SSE streaming events observable via curl with `--no-buffer`

### ✅ VI. Reusable Intelligence (Agent Skills)
- **Status**: PASS (proactive skill usage)
- **Evidence**: Will leverage existing skills during implementation:
  - **multi_user_data_isolation**: JWT verification, user-scoped queries pattern
  - **error_handler**: Standardized exception handling for OpenAI API, MCP, database errors
  - **ux_logic_anchor**: Consistent error message formatting for frontend display

### ✅ VII. Stateless Security (JWT Authentication)
- **Status**: PASS
- **Evidence**:
  - JWT token verification via BETTER_AUTH_SECRET (FR-001)
  - User_id extracted from 'sub' claim (FR-002)
  - All resources filtered by user_id (FR-004)
  - Return 404 for unauthorized access (prevent resource enumeration)
  - Token never exposed in agent instructions (FR-033, Constraint #5)

### 📊 Constitution Compliance Summary

| Principle | Compliance | Notes |
|-----------|------------|-------|
| SDD-RI | ✅ PASS | Following specification → planning → tasks → implementation workflow |
| Pythonic | ✅ PASS | Python 3.13+, async/await, modern type hints, tool-enforced quality |
| Persistent State | ✅ PASS | Neon PostgreSQL, SQLModel, user_id isolation, CASCADE constraints |
| Type Safety | ✅ PASS | Full type hints, docstrings, Pydantic validation |
| Terminal Verify | ✅ PASS | REST API + SSE streaming, curl-testable, proper status codes |
| Reusable Skills | ✅ PASS | Leveraging multi_user_data_isolation, error_handler, ux_logic_anchor |
| Stateless JWT | ✅ PASS | Token verification, user_id scoping, token security (headers-only) |

**All gates PASSED. Ready to proceed with Phase 0 research.**

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: New standalone backend service in `chatbot-backend/` directory at repository root. This is a separate service from the existing TODO backend, communicating via the TODO MCP Server as intermediary.

```text
chatbot-backend/
├── pyproject.toml              # UV package manager configuration (uv init)
├── .env.example                # Environment variable template
├── .env                        # Local config (git-ignored)
├── README.md                   # Setup and usage instructions
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization, /api/chatkit endpoint
│   ├── config.py               # Environment variable loading, validation
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt.py              # JWT token verification, user_id extraction
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat_thread.py      # SQLModel for chat_threads table
│   │   ├── chat_message.py     # SQLModel for chat_messages table
│   │   └── request_context.py  # RequestContext dataclass (user_id, token, request)
│   │
│   ├── store/
│   │   ├── __init__.py
│   │   └── neon_store.py       # NeonPostgresStore(Store[RequestContext])
│   │
│   ├── server/
│   │   ├── __init__.py
│   │   └── chatkit_server.py   # ChatKitServer subclass with respond() method
│   │
│   └── utils/
│       ├── __init__.py
│       ├── agent_factory.py    # Create Agent with MCP client, user instructions
│       └── errors.py           # Custom exception classes, error formatting
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures (test DB, mock MCP server)
│   │
│   ├── unit/
│   │   ├── test_jwt.py         # Token verification, user_id extraction
│   │   ├── test_agent_factory.py   # Agent creation, instruction formatting
│   │   └── test_store.py       # Store methods (load/save thread, items)
│   │
│   ├── integration/
│   │   ├── test_chatkit_flow.py    # End-to-end: message → agent → response
│   │   ├── test_mcp_integration.py # Agent calling MCP tools
│   │   └── test_persistence.py     # Thread/message database operations
│   │
│   └── fixtures/
│       ├── sample_jwt.py       # Valid/invalid test tokens
│       └── sample_messages.py  # ChatKit protocol test payloads
│
└── alembic/                    # Database migration tool
    ├── versions/               # Migration scripts
    │   └── 001_create_chat_tables.py
    ├── env.py                  # Alembic environment config
    └── alembic.ini             # Alembic settings
```

**Rationale for Separation**:
- **Port Isolation**: Chatbot backend (8001) vs TODO backend (9000) - no port conflicts
- **Independent Deployment**: Can scale/update chatbot service independently
- **Dependency Isolation**: OpenAI Agents SDK / ChatKit SDK don't affect TODO backend
- **Clear Responsibility**: TODO backend handles CRUD + auth, chatbot handles conversation + AI
- **MCP as Bridge**: MCP server provides clean API boundary between services

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations to justify.** All design decisions align with Constitution principles.

---

## Phase 0: Research & Design Decisions

*This phase resolves all technical unknowns identified in Technical Context.*

### Decision 1: ChatKit Server Architecture Pattern

**Question**: How to structure the ChatKitServer with custom respond() method and Store implementation?

**Research Findings** (from Context7 + OpenAI ChatKit Advanced Samples):
- ChatKitServer is an abstract base class requiring `respond()` method implementation
- `respond()` receives `ThreadMetadata`, `UserMessageItem`, and generic `RequestContext`
- Must yield `ThreadStreamEvent` objects (e.g., `ThreadItemDoneEvent` wrapping `AssistantMessageItem`)
- Store interface requires async methods: `load_thread`, `save_thread`, `load_thread_items`, `add_thread_item`, `save_item`, `delete_thread`
- Can use `AgentContext` from `chatkit.agents` to bridge with OpenAI Agents SDK
- `stream_agent_response()` helper converts agent events → ChatKit events

**Decision**: Implement custom `ChatbotServer(ChatKitServer[RequestContext])` class:
```python
class ChatbotServer(ChatKitServer[RequestContext]):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # 1. Load thread history (last 20 messages)
        items = await self.store.load_thread_items(thread.id, None, 20, "asc", context)
        
        # 2. Create agent with user-specific instructions
        agent = create_agent_for_user(context.user_id, context.token)
        
        # 3. Convert ChatKit items → agent input format
        agent_input = await chatkit_to_agent_input(items.data, input_message)
        
        # 4. Create AgentContext for streaming
        agent_ctx = AgentContext(thread=thread, store=self.store, request_context=context)
        
        # 5. Run agent with streaming
        result = Runner.run_streamed(agent, agent_input, context=agent_ctx)
        
        # 6. Stream events back to frontend
        async for event in stream_agent_response(agent_ctx, result):
            yield event
```

**Rationale**:
- Leverages ChatKit's built-in integration with OpenAI Agents SDK
- `AgentContext` provides thread/store access to agent during execution
- `stream_agent_response()` handles event conversion automatically
- Keeps respond() method focused on orchestration, not implementation details

**Alternatives Considered**:
- Manual event generation (rejected: reinvents ChatKit's built-in patterns)
- Non-streaming responses (rejected: violates SC-001, SC-006 latency requirements)

---

### Decision 2: NeonPostgresStore Implementation Strategy

**Question**: How to implement Store[RequestContext] interface for Neon PostgreSQL?

**Research Findings**:
- Store interface has 11 required methods (load/save thread, items, attachments)
- PostgreSQL implementation pattern from ChatKit docs:
  - Separate tables for threads and items
  - JSON column for flexible metadata storage
  - User_id filtering enforced in SQL WHERE clauses
- RequestContext must contain user_id for isolation
- Can use asyncpg or psycopg2 for database connectivity
- SQLModel provides type-safe model definitions

**Decision**: Implement `NeonPostgresStore(Store[RequestContext])` with:
```python
class NeonPostgresStore(Store[RequestContext]):
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
    
    async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
        # Query: SELECT * FROM chat_threads WHERE id = ? AND user_id = ?
        async with AsyncSession(self.engine) as session:
            stmt = select(ChatThread).where(
                ChatThread.id == thread_id,
                ChatThread.user_id == context.user_id
            )
            result = await session.execute(stmt)
            thread = result.scalar_one_or_none()
            if not thread:
                raise NotFoundError(f"Thread {thread_id} not found")
            return ThreadMetadata(id=thread.id, created_at=thread.created_at, ...)
    
    async def save_thread(self, thread: ThreadMetadata, context: RequestContext) -> None:
        # INSERT thread with user_id from context
        async with AsyncSession(self.engine) as session:
            chat_thread = ChatThread(
                id=thread.id,
                user_id=context.user_id,  # Enforce isolation
                created_at=thread.created_at,
                ...
            )
            session.add(chat_thread)
            await session.commit()
    
    # ... implement remaining 9 methods
```

**Rationale**:
- SQLModel + asyncpg provides type-safe async database operations
- User_id isolation enforced at query level (satisfies FR-004, SC-003)
- ThreadMetadata ↔ ChatThread model conversion keeps ChatKit types separate from ORM
- AsyncSession for proper connection pooling in async context

**Alternatives Considered**:
- Raw SQL with asyncpg (rejected: loses type safety, more error-prone)
- In-memory store (rejected: doesn't meet persistence requirement SC-004)
- Shared ORM models (rejected: couples ChatKit types to database schema)

---

### Decision 3: Agent Creation with MCP Client Integration

**Question**: How to create Agent instances with GPT-4o-mini, user instructions, and MCP client?

**Research Findings** (from Context7 + OpenAI Agents SDK):
- Agent constructor accepts: `name`, `instructions`, `model`, `mcp_servers` (or `mcp_clients`)
- MCP servers can be HTTP-based via `MCPServerStreamableHttp`
- HTTP servers accept `url`, `headers`, and optional `cache_tools_list` parameter
- Instructions can be dynamic strings (can include user_id for context)
- Agent model defaults to "gpt-4o-mini" if not specified
- MCP client forwards `headers` to all tool calls

**Decision**: Factory function `create_agent_for_user()`:
```python
async def create_agent_for_user(user_id: str, token: str) -> Agent:
    # Create MCP client with auth headers
    mcp_client = MCPServerStreamableHttp(
        name="todo",
        params={
            "url": "http://localhost:3000/mcp",
            "headers": {"Authorization": f"Bearer {token}"}
        },
        cache_tools_list=True  # Avoid re-fetching tools on every request
    )
    
    # Create agent with user-specific instructions
    agent = Agent(
        name="TaskAssistant",
        model="gpt-4o-mini",
        instructions=f"""
You are a helpful task management assistant for user {user_id}.

You have access to todo management tools. When the user asks about their tasks,
use the appropriate tool and ALWAYS pass user_id={user_id} as a parameter.

Available tools and when to use them:
- list_tasks: Show user's tasks (pending/completed/all)
- add_task: Create new task with title and optional description
- complete_task: Toggle task completion status
- update_task: Modify existing task title or description
- delete_task: Permanently remove a task

Be conversational and helpful. Confirm actions after completing them.
        """.strip(),
        mcp_servers=[mcp_client]
    )
    
    return agent
```

**Rationale**:
- Token passed via MCP headers (satisfies FR-017, Constraint #5: never in instructions)
- User_id embedded in instructions ensures agent always includes it in tool calls (FR-019)
- Model explicitly set to "gpt-4o-mini" (FR-011)
- `cache_tools_list=True` reduces latency for repeated requests
- Instructions provide tool usage guidance, improving accuracy (contributes to SC-010)

**Alternatives Considered**:
- Static agent reused across requests (rejected: can't customize per-user instructions, security risk)
- Token in tool parameters (rejected: violates token security constraint, not supported by MCP)
- User_id in RequestContext only (rejected: agent wouldn't know to include it in tool calls)

---

### Decision 4: JWT Token Verification Strategy

**Question**: How to verify Better Auth JWT tokens and extract user_id?

**Research Findings**:
- Better Auth uses HS256 algorithm with BETTER_AUTH_SECRET environment variable
- JWT token contains 'sub' claim with user_id value
- python-jose library provides `jwt.decode()` with signature verification
- FastAPI dependency injection can extract Authorization header
- Invalid/expired tokens should return 401 Unauthorized

**Decision**: JWT middleware with FastAPI dependency:
```python
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Header
from typing import Annotated

def verify_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract and verify JWT token, return user_id"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")
    
    token = authorization.removeprefix("Bearer ")
    
    try:
        payload = jwt.decode(
            token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Usage in endpoint
@app.post("/api/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: Annotated[str, Depends(verify_token)]
):
    context = RequestContext(user_id=user_id, token=request.headers["authorization"], request=request)
    result = await server.process(await request.body(), context)
    ...
```

**Rationale**:
- FastAPI dependency injection ensures all requests are authenticated (FR-001)
- Returns 401 for missing/invalid tokens (FR-003)
- Extracts user_id for request scoping (FR-002)
- Keeps token in header (FR-033: never in agent instructions/logs)

**Alternatives Considered**:
- Middleware-based verification (rejected: less explicit, harder to test)
- Manual header parsing in endpoint (rejected: duplicates code across endpoints)
- No verification (rejected: violates security principles VII)

---

### Decision 5: Streaming Response Handling

**Question**: How to return ChatKit StreamingResult from FastAPI endpoint?

**Research Findings** (from ChatKit Advanced Samples):
- ChatKitServer.process() returns either `StreamingResult` or `StaticResult`
- StreamingResult is an async generator of SSE events
- FastAPI StreamingResponse accepts async generators
- Media type must be "text/event-stream" for SSE
- StaticResult has `.json` property for non-streaming responses

**Decision**: Conditional response based on result type:
```python
from fastapi.responses import StreamingResponse, Response
from chatkit.server import StreamingResult

@app.post("/api/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: Annotated[str, Depends(verify_token)]
):
    # Create request context
    context = RequestContext(
        user_id=user_id,
        token=request.headers["authorization"],
        request=request
    )
    
    # Process ChatKit protocol message
    result = await server.process(await request.body(), context)
    
    # Return appropriate response type
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    else:
        return Response(content=result.json, media_type="application/json")
```

**Rationale**:
- ChatKit's built-in StreamingResult handles SSE formatting (FR-006, FR-027)
- FastAPI StreamingResponse provides HTTP streaming support
- Conditional logic handles both streaming and non-streaming operations (FR-008, FR-028)
- Single endpoint delegates all protocol handling to ChatKitServer (FR-029)

**Alternatives Considered**:
- Manual SSE formatting (rejected: violates FR-006, reinvents ChatKit functionality)
- Separate streaming/non-streaming endpoints (rejected: complicates frontend, violates FR-026)

---

### Decision 6: Database Schema Design

**Question**: What SQLModel definitions are needed for chat persistence?

**Research Findings**:
- Spec requires two tables: chat_threads, chat_messages (FR-021, FR-022)
- chat_threads: UUID primary key, user_id foreign key, title (optional), timestamps
- chat_messages: BIGSERIAL primary key, thread_id foreign key, role check constraint, content, timestamp
- Indexes on user_id (threads) and thread_id + created_at (messages) for performance (FR-024)
- CASCADE DELETE for user → threads → messages cleanup (FR-023)

**Decision**: SQLModel class definitions:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class ChatThread(SQLModel, table=True):
    __tablename__ = "chat_threads"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    messages: list["ChatMessage"] = Relationship(back_populates="thread", cascade_delete=True)

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment
    thread_id: str = Field(foreign_key="chat_threads.id", ondelete="CASCADE", index=True)
    role: str = Field(sa_column_kwargs={"check": "role IN ('user', 'assistant', 'system')"})
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    thread: ChatThread = Relationship(back_populates="messages")
```

**Alembic Migration**:
```python
# alembic/versions/001_create_chat_tables.py
def upgrade():
    op.create_table(
        "chat_threads",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
    )
    op.create_index("idx_chat_threads_user_id", "chat_threads", ["user_id"])
    
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("thread_id", sa.Text(), sa.ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_role"),
    )
    op.create_index("idx_chat_messages_thread_id", "chat_messages", ["thread_id"])
    op.create_index("idx_chat_messages_created_at", "chat_messages", ["created_at"])
```

**Rationale**:
- UUID for thread IDs (globally unique, no collision risk) (FR-025)
- BIGSERIAL for message IDs (sequential, efficient for ordering) (FR-025)
- Composite index on (thread_id, created_at) for efficient message retrieval (FR-024)
- CHECK constraint on role enum values prevents invalid data
- CASCADE DELETE ensures cleanup when users deleted (FR-023)
- SQLModel relationships enable type-safe joins

**Alternatives Considered**:
- Integer thread IDs (rejected: collision risk in distributed system)
- JSON column for message content (rejected: loses type safety, harder to query)
- No indexes (rejected: violates FR-024, poor performance for large threads)

---

### Decision 7: Error Handling Strategy

**Question**: How to handle errors from OpenAI API, MCP server, and database operations?

**Research Findings**:
- OpenAI SDK raises exceptions for API errors (rate limits, invalid requests)
- MCP client can fail due to connection errors or tool call failures
- Database operations can fail (connection errors, constraint violations)
- Spec requires meaningful error messages for all scenarios (SC-008)
- User-friendly messages without exposing sensitive details (FR-038)

**Decision**: Centralized error handling with custom exception classes:
```python
class ChatbotError(Exception):
    """Base exception for chatbot errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AgentError(ChatbotError):
    """Errors from OpenAI Agent operations"""
    pass

class MCPError(ChatbotError):
    """Errors from MCP server communication"""
    pass

class StorageError(ChatbotError):
    """Errors from database operations"""
    pass

# Error handler in respond() method
try:
    result = Runner.run_streamed(agent, input, context=agent_ctx)
    async for event in stream_agent_response(agent_ctx, result):
        yield event
except OpenAIError as e:
    logger.error(f"OpenAI API error: {e}", exc_info=True)
    raise AgentError("Assistant is temporarily unavailable. Please try again.", 503)
except HTTPError as e:
    logger.error(f"MCP server error: {e}", exc_info=True)
    raise MCPError("Task management features are temporarily unavailable.", 503)
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}", exc_info=True)
    # Don't fail streaming response if only persistence failed
    logger.warning("Message may not be persisted due to database error")
```

**Error Response Format**:
```python
{
    "error": {
        "type": "agent_error",  # error_type
        "message": "Assistant is temporarily unavailable. Please try again.",  # user-facing
        "request_id": "uuid-here"  # for debugging
    }
}
```

**Rationale**:
- Custom exception hierarchy provides typed error handling
- User-friendly messages don't expose internals (FR-038, SC-008)
- Logging includes stack traces for debugging (FR-034, FR-038)
- Database errors don't block streaming (satisfies edge case requirement)
- 503 status indicates temporary service unavailability
- Request ID enables error tracking across distributed system

**Alternatives Considered**:
- Generic exceptions (rejected: loses error context, harder to handle appropriately)
- Detailed error messages (rejected: exposes system internals, security risk)
- Fail-fast on database errors (rejected: violates edge case requirement)

---

### Decision 8: Configuration Management

**Question**: How to manage environment variables and validate required configuration at startup?

**Research Findings**:
- python-dotenv loads .env files into os.environ
- Pydantic BaseSettings provides typed configuration with validation
- FastAPI lifespan events allow startup validation
- Spec requires validation of DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, MCP_SERVER_URL (FR-040)

**Decision**: Pydantic Settings class with startup validation:
```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Required settings
    database_url: str = Field(..., env="DATABASE_URL")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    better_auth_secret: str = Field(..., env="BETTER_AUTH_SECRET")
    mcp_server_url: str = Field(default="http://localhost:3000/mcp", env="MCP_SERVER_URL")
    
    # Optional settings with defaults
    port: int = Field(default=8001, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    openai_timeout: int = Field(default=30, env="OPENAI_TIMEOUT")
    mcp_timeout: int = Field(default=10, env="MCP_TIMEOUT")
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

# Startup validation
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        settings = Settings()  # Validates all required env vars
        logger.info("Configuration validated successfully")
        logger.info(f"MCP Server URL: {settings.mcp_server_url}")
        logger.info(f"Database URL: {settings.database_url.split('@')[0]}@...")  # Don't log password
    except ValidationError as e:
        logger.error(f"Configuration error: {e}")
        raise RuntimeError("Missing required environment variables")
    
    yield

app = FastAPI(lifespan=lifespan)
```

**.env.example**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here

# MCP Server (optional, defaults to localhost:3000)
MCP_SERVER_URL=http://localhost:3000/mcp

# Server settings (optional)
PORT=8001
HOST=0.0.0.0

# Timeouts (optional, in seconds)
OPENAI_TIMEOUT=30
MCP_TIMEOUT=10
```

**Rationale**:
- Pydantic validates types and required fields automatically (FR-040)
- Lifespan events ensure startup fails fast if misconfigured
- .env.example documents all configuration options
- Defaults provided for non-critical settings
- Passwords never logged (security best practice)
- Timeout configuration supports FR-041

**Alternatives Considered**:
- os.getenv() with manual validation (rejected: verbose, error-prone, no type safety)
- Config file (YAML/JSON) (rejected: environment variables preferred for 12-factor apps)
- Lazy validation (rejected: runtime errors harder to debug than startup failures)

---

## Phase 0 Summary: All Technical Unknowns Resolved

✅ **Decision 1**: ChatKitServer architecture with custom respond() method  
✅ **Decision 2**: NeonPostgresStore implementation strategy with SQLModel  
✅ **Decision 3**: Agent creation with MCP client integration and dynamic instructions  
✅ **Decision 4**: JWT verification using FastAPI dependencies  
✅ **Decision 5**: Streaming response handling with conditional FastAPI responses  
✅ **Decision 6**: Database schema with SQLModel and Alembic migrations  
✅ **Decision 7**: Error handling with custom exception hierarchy  
✅ **Decision 8**: Configuration management with Pydantic Settings

**No NEEDS CLARIFICATION items remain. Ready to proceed to Phase 1 (data model, contracts, quickstart).**


---

## Phase 1: Data Model, Contracts & Setup

*This phase generates concrete artifacts ready for implementation.*

### Artifacts Created

✅ **data-model.md**: Complete entity definitions
- ChatThread (UUID PK, user_id FK, title, timestamps)
- ChatMessage (BIGSERIAL PK, thread_id FK, role CHECK, content)
- RequestContext (dataclass for per-request auth)
- SQLModel class definitions
- Alembic migration scripts
- Data isolation patterns
- Testing data samples

✅ **contracts/chatkit-endpoint.md**: API specification
- POST /api/chatkit endpoint documentation
- ChatKit protocol message formats
- Request/response examples (streaming & non-streaming)
- Error response formats (401, 404, 503, 500)
- Authentication flow diagram
- Performance characteristics
- curl and Python testing examples
- CORS configuration

✅ **quickstart.md**: Developer setup guide
- Prerequisites checklist
- Step-by-step UV project initialization
- Dependency installation commands
- Environment configuration (.env template)
- Project structure creation
- Core component implementation (config, JWT, FastAPI app)
- Database migration setup
- Server startup commands
- Testing procedures
- Troubleshooting guide

✅ **Agent context updated**: CLAUDE.md
- Added: FastAPI, OpenAI Agents SDK, ChatKit Python SDK
- Added: Python 3.13+ with modern async/await patterns
- Updated: Active Technologies section

---

## Phase 1 Summary: Implementation-Ready Artifacts

All Phase 1 deliverables complete:
- ✅ **Data model**: SQLModel classes, migration scripts, isolation patterns
- ✅ **API contracts**: ChatKit endpoint specification with examples
- ✅ **Quickstart**: Complete setup guide from init to first request
- ✅ **Agent context**: Technologies documented for AI assistance

**Ready to proceed to Phase 2 (`/sp.tasks`)**: Task breakdown for implementation.

---

## Architecture Diagrams

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

---

## Key Design Principles Applied

### 1. Separation of Concerns
- **ChatKit Server**: Conversation management, protocol handling
- **Agent Factory**: Agent creation with MCP client setup
- **NeonPostgresStore**: Database operations with user isolation
- **JWT Middleware**: Authentication before business logic

### 2. Security Through Architecture
- **Token Never in Instructions**: Passed via HTTP headers only
- **User Isolation at Query Level**: WHERE user_id = ? in all SELECT statements
- **404 for Unauthorized**: Prevents resource enumeration
- **Stateless Design**: No shared state between requests

### 3. Performance Through Design
- **Streaming First**: SSE streaming for real-time user experience
- **Async Throughout**: Async database, HTTP, agent operations
- **Index Strategy**: Composite indexes for common query patterns
- **Connection Pooling**: SQLAlchemy async engine with pool

### 4. Type Safety Through Layers
- **Pydantic Settings**: Environment variable validation at startup
- **SQLModel**: Type-safe ORM with Pydantic integration
- **Dataclasses**: RequestContext with explicit types
- **Type Hints**: All functions fully typed (Python 3.13 union syntax)

---

## Risk Mitigation

### Identified Risks & Mitigations

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| **OpenAI API downtime** | Users can't chat | Catch exceptions, return 503 with clear message. Consider fallback agent or queue. |
| **MCP server downtime** | Agent can't call tools | Graceful degradation: agent responds without tools, inform user task management unavailable. |
| **Database connection loss** | Can't persist history | Don't block streaming; log error, continue chat. Implement retry logic with exponential backoff. |
| **Token expiration mid-conversation** | Request fails with 401 | Frontend detects 401, refreshes token, retries request. Clear user communication. |
| **Long agent responses (>30s)** | Timeout or poor UX | Implement timeout handling, stream partial responses, allow interruption. |
| **Concurrent user spike** | Performance degradation | Stateless design enables horizontal scaling. Monitor latency, add instances as needed. |
| **Large thread history (100+ messages)** | Slow load times | Pagination (last 20 messages). Lazy loading on scroll. Consider archiving old messages. |

---

## Success Validation Checklist

Before marking implementation complete, verify:

### Functional Requirements (41 FRs)
- [ ] FR-001 to FR-004: JWT authentication and user_id extraction working
- [ ] FR-005 to FR-010: ChatKitServer with custom respond() implemented
- [ ] FR-011 to FR-015: Agent creation with GPT-4o-mini and streaming
- [ ] FR-016 to FR-020: MCP client integration with token forwarding
- [ ] FR-021 to FR-025: Database persistence with CASCADE DELETE
- [ ] FR-026 to FR-029: Single ChatKit endpoint with streaming/static responses
- [ ] FR-030 to FR-033: Request context with token security
- [ ] FR-034 to FR-038: Error handling and logging
- [ ] FR-039 to FR-041: Configuration validation

### Success Criteria (10 SCs)
- [ ] SC-001: First token within 3 seconds ⏱️
- [ ] SC-002: 100% MCP tool call accuracy ✅
- [ ] SC-003: 0% cross-user access 🔒
- [ ] SC-004: 100% message persistence 💾
- [ ] SC-005: 10 concurrent users without degradation 👥
- [ ] SC-006: Visible content within 1 second ⚡
- [ ] SC-007: 0% auth bypass vulnerabilities 🛡️
- [ ] SC-008: 100% meaningful error messages 📝
- [ ] SC-009: 100+ messages per thread 📚
- [ ] SC-010: 90%+ natural language accuracy 🤖

### User Stories (3 Priorities)
- [ ] P1: Basic Chat Interaction - Send message → Receive streamed response
- [ ] P2: Task Management - Natural language commands → MCP tool calls
- [ ] P3: Persistent History - Resume conversations across sessions

### Edge Cases (8 Scenarios)
- [ ] OpenAI API unavailable → User-friendly error
- [ ] MCP server down → Graceful degradation
- [ ] Token expires → 401 with refresh prompt
- [ ] Agent timeout (>30s) → Timeout handling
- [ ] Database failure → Stream continues, log error
- [ ] Malformed message → Validation error
- [ ] Concurrent requests → Independent handling
- [ ] Unauthorized thread access → 404 Not Found

---

## Conclusion

**Planning phase complete.** All technical decisions documented, architectures designed, and implementation artifacts created. Ready to proceed to `/sp.tasks` for detailed task breakdown.

**Key Deliverables**:
- 8 technical decisions with rationales and alternatives
- Complete data model with SQLModel definitions
- API contract with request/response examples
- Comprehensive quickstart guide
- Architecture diagrams and flow charts
- Risk mitigation strategies
- Success validation checklist

**Next Command**: `/sp.tasks` to generate actionable implementation tasks.

