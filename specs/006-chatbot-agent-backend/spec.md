# Feature Specification: Chatbot Backend with OpenAI Agents and ChatKit MCP Integration

**Feature Branch**: `006-chatbot-agent-backend`
**Created**: 2026-02-02
**Status**: Draft
**Input**: User description: "Build a FastAPI-based chatbot backend that uses OpenAI Agents SDK and ChatKit Python to provide an AI assistant that can manage users' todos through MCP (Model Context Protocol) integration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Chat Interaction with AI Assistant (Priority: P1)

As an authenticated user, I want to send messages to an AI assistant and receive real-time streamed responses so that I can have natural conversations about my tasks.

**Why this priority**: This is the foundation of the chatbot - users must be able to communicate with the AI before any task management features can be useful. Without this, no other functionality works.

**Independent Test**: Can be fully tested by sending a simple message (e.g., "Hello") to the chatbot endpoint and verifying that a streamed AI response is received in real-time. Delivers immediate value by providing an interactive chat experience.

**Acceptance Scenarios**:

1. **Given** a logged-in user with valid Better Auth token, **When** user sends "Hello" message to /api/chatkit endpoint, **Then** system streams AI assistant response in real-time with proper SSE format
2. **Given** a user without authentication token, **When** user attempts to send message, **Then** system returns 401 Unauthorized error
3. **Given** a user sends a message, **When** response is being generated, **Then** frontend receives content_delta events showing typing effect in real-time
4. **Given** a long AI response (>100 words), **When** generation occurs, **Then** response streams token-by-token without waiting for complete generation
5. **Given** an invalid token is provided, **When** request is made, **Then** system returns 401 Unauthorized with clear error message

---

### User Story 2 - Task Management Through Conversational AI (Priority: P2)

As a user having a conversation with the AI assistant, I want the assistant to manage my todos through natural language commands so that I don't need to switch to a separate UI for task operations.

**Why this priority**: This adds the core value proposition of task management to the chat interface. Depends on P1 (basic chat) being functional. Users can already manage tasks through the main UI, so this provides an alternative conversational interface.

**Independent Test**: Can be tested by asking the assistant "Show me my tasks" or "Add a new task: Buy groceries" and verifying that the assistant calls appropriate MCP tools and returns accurate responses about task operations. Delivers task management value through natural conversation.

**Acceptance Scenarios**:

1. **Given** a user asks "Show me my incomplete tasks", **When** assistant processes request, **Then** system calls list_tasks MCP tool with user_id and status="pending", and responds with formatted list of user's pending tasks
2. **Given** a user says "Add a new task: Buy groceries", **When** assistant processes request, **Then** system calls add_task MCP tool with user_id and task details, and confirms task creation with task ID
3. **Given** a user requests "Mark task 5 as complete", **When** assistant processes request, **Then** system calls complete_task MCP tool with user_id and task_id=5, and confirms completion
4. **Given** a user asks to update task 3, **When** assistant processes request, **Then** system calls update_task MCP tool with appropriate parameters
5. **Given** a user asks to delete task 7, **When** assistant processes request, **Then** system calls delete_task MCP tool and confirms deletion
6. **Given** a user tries to access another user's task (task owned by different user_id), **When** MCP tool is called, **Then** backend enforces isolation and returns "Task not found" error

---

### User Story 3 - Persistent Conversation History (Priority: P3)

As a user, I want my conversation history with the assistant to be saved so that I can resume conversations across sessions and the assistant remembers our previous interactions.

**Why this priority**: Enhances user experience by providing continuity, but chat functionality works without it. Users can still interact with the assistant in P1/P2 even if history isn't persisted. This is a quality-of-life improvement rather than core functionality.

**Independent Test**: Can be tested by having a conversation, closing/reopening the chat, and verifying that previous messages are loaded and the conversation can continue with context. Delivers persistent memory across sessions.

**Acceptance Scenarios**:

1. **Given** a user starts a new conversation, **When** first message is sent, **Then** system creates new thread in chat_threads table with unique ID and user_id
2. **Given** an ongoing conversation thread, **When** user sends message, **Then** system stores both user message and assistant response in chat_messages table linked to thread_id
3. **Given** a user has previous conversation history, **When** user requests to load thread, **Then** system retrieves messages from chat_messages ordered by created_at
4. **Given** a user opens chat interface, **When** loading recent conversations, **Then** system returns list of user's threads ordered by updated_at (most recent first)
5. **Given** a thread has 100+ messages, **When** loading thread, **Then** system loads last 20 messages initially with option to load more (pagination)
6. **Given** user account is deleted, **When** CASCADE DELETE is triggered, **Then** all user's chat_threads and related chat_messages are automatically removed

---

### Edge Cases

- What happens when OpenAI API is unavailable or returns an error? System should catch exceptions and return user-friendly error message like "Assistant is temporarily unavailable. Please try again."
- What happens when MCP server is down? System should gracefully handle connection errors and inform user that task management features are temporarily unavailable
- What happens when a user's Better Auth token expires mid-conversation? System returns 401 and prompts frontend to refresh token
- What happens when agent takes longer than 30 seconds to respond? System should include timeout handling and inform user if response generation fails
- What happens when database connection fails during message persistence? System logs error but doesn't block streaming response (chat works, history may be lost for that turn)
- What happens when user sends malformed ChatKit protocol message? System validates input and returns appropriate error response
- What happens with concurrent requests from same user? System handles each request independently with proper isolation
- What happens when user tries to access thread belonging to different user? System enforces user_id filtering and returns 404 Not Found

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Authorization:**
- **FR-001**: System MUST validate Better Auth JWT tokens from Authorization header on every request
- **FR-002**: System MUST extract user_id from validated JWT token and use it for all user-scoped operations
- **FR-003**: System MUST return 401 Unauthorized for requests with missing or invalid authentication tokens
- **FR-004**: System MUST ensure all database queries filter by authenticated user's user_id to enforce data isolation

**ChatKit Server Integration:**
- **FR-005**: System MUST implement ChatKitServer with custom respond() method that yields ThreadStreamEvent objects
- **FR-006**: System MUST use ChatKit's built-in StreamingResult for streaming responses (no manual StreamingResponse wrapper)
- **FR-007**: System MUST implement custom NeonPostgresStore extending ChatKit Store interface for database operations
- **FR-008**: System MUST handle both streaming and non-streaming ChatKit protocol messages
- **FR-009**: System MUST create new thread when user initiates conversation without existing thread_id
- **FR-010**: System MUST load existing thread history (last 20 messages) when thread_id is provided

**OpenAI Agent Configuration:**
- **FR-011**: System MUST create Agent instances with GPT-4o-mini model for each conversation
- **FR-012**: System MUST configure agent with user-specific instructions that include the authenticated user_id
- **FR-013**: System MUST integrate MCP client with agent's mcp_clients parameter
- **FR-014**: System MUST use Runner.run_streamed() for generating responses with real-time streaming
- **FR-015**: System MUST convert agent stream events to ChatKit ThreadStreamEvent format

**MCP Integration:**
- **FR-016**: System MUST connect to TODO MCP Server at http://localhost:3000
- **FR-017**: System MUST pass authentication token via MCP client headers (Authorization: Bearer <token>)
- **FR-018**: Agent MUST have access to these MCP tools: list_tasks, add_task, complete_task, update_task, delete_task
- **FR-019**: Agent instructions MUST specify to always pass user_id parameter when calling MCP tools
- **FR-020**: System MUST handle MCP tool call errors gracefully and provide user-friendly error messages

**Data Persistence:**
- **FR-021**: System MUST store conversation threads in chat_threads table with id, user_id, title, timestamps
- **FR-022**: System MUST store individual messages in chat_messages table with thread_id, role, content, timestamp
- **FR-023**: System MUST enforce foreign key constraints with CASCADE DELETE for data consistency
- **FR-024**: System MUST create indexes on user_id (chat_threads), thread_id (chat_messages), and created_at (chat_messages) for query performance
- **FR-025**: System MUST generate UUID for chat thread IDs and auto-increment for message IDs

**API Endpoints:**
- **FR-026**: System MUST provide single POST /api/chatkit endpoint that accepts ChatKit protocol messages
- **FR-027**: System MUST return StreamingResult with media_type="text/event-stream" for streaming responses
- **FR-028**: System MUST return JSON response for non-streaming ChatKit operations
- **FR-029**: System MUST delegate all ChatKit protocol handling to ChatKitServer.process() method

**Context Management:**
- **FR-030**: System MUST create per-request context dict containing user_id, token, and request object
- **FR-031**: System MUST pass context to ChatKit server respond() method for agent and MCP configuration
- **FR-032**: System MUST use context to initialize MCP client with appropriate Authorization headers
- **FR-033**: System MUST ensure token is never exposed in agent instructions or logs (only in HTTP headers)

**Error Handling & Logging:**
- **FR-034**: System MUST log all requests with request ID, user_id, and timestamp for debugging
- **FR-035**: System MUST catch and handle OpenAI API errors with user-friendly messages
- **FR-036**: System MUST catch and handle MCP connection/tool errors without crashing
- **FR-037**: System MUST return structured error responses with appropriate HTTP status codes
- **FR-038**: System MUST log errors with stack traces for debugging while hiding sensitive details from users

**Configuration:**
- **FR-039**: System MUST load configuration from environment variables (.env file)
- **FR-040**: System MUST validate required environment variables at startup (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, MCP_SERVER_URL)
- **FR-041**: System MUST support configurable timeouts for OpenAI API and MCP server calls

### Key Entities

- **ChatThread**: Represents a conversation session between user and assistant
  - Attributes: unique ID (UUID), user_id (owner), optional title, creation and update timestamps
  - Relationships: Belongs to User (via user_id), has many ChatMessages
  - Lifecycle: Created on first message, updated on each new message, deleted when user is deleted (CASCADE)

- **ChatMessage**: Represents a single message in a conversation thread
  - Attributes: unique ID (auto-increment), thread_id, role (user/assistant/system), content text, timestamp
  - Relationships: Belongs to ChatThread (via thread_id)
  - Lifecycle: Created when user sends message or assistant generates response, deleted when thread is deleted (CASCADE)

- **RequestContext**: Runtime object containing per-request authentication and configuration
  - Attributes: user_id (extracted from JWT), token (full JWT), request object
  - Relationships: Used to configure MCP client and agent for current request
  - Lifecycle: Created per request, exists only in memory during request processing

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send chat message and receive first token of AI response within 3 seconds of request
- **SC-002**: AI assistant successfully executes MCP tool calls (list/add/complete/update/delete tasks) with 100% accuracy for valid requests
- **SC-003**: System enforces user data isolation such that 0% of requests can access other users' chat history or tasks
- **SC-004**: Chat history persists across sessions such that 100% of messages are retrievable after page reload
- **SC-005**: System handles 10 concurrent users sending messages simultaneously without response degradation
- **SC-006**: Streaming responses deliver visible content to user within 1 second of agent starting generation
- **SC-007**: Token authentication works end-to-end with 0% authorization bypass vulnerabilities
- **SC-008**: System provides meaningful error messages for 100% of failure scenarios (invalid token, API errors, MCP errors)
- **SC-009**: Chat conversations support minimum 100 messages per thread without performance issues
- **SC-010**: Agent correctly interprets task management requests in natural language with 90%+ accuracy (e.g., "show my tasks", "add new task", "mark as done")

## Assumptions *(mandatory)*

1. **Frontend Implementation**: Assumes Next.js frontend (port 3000) with ChatKit UI components is already implemented and functional
2. **TODO Backend**: Assumes existing TODO REST API (port 9000) is running and accessible for MCP server to call
3. **TODO MCP Server**: Assumes existing MCP server (port 3000) is running with all 5 tools (list/add/complete/update/delete) properly implemented
4. **Better Auth Setup**: Assumes Better Auth is already configured and generating valid JWT tokens with user_id in 'sub' claim
5. **Database Access**: Assumes connection credentials for Neon PostgreSQL database are available and database is accessible
6. **OpenAI API Key**: Assumes valid OpenAI API key with access to GPT-4o-mini model is available
7. **Network Access**: Assumes backend can make HTTP requests to MCP server and OpenAI API endpoints
8. **Port Availability**: Assumes port 8001 is available and not blocked by firewall for backend service
9. **JWT Secret**: Assumes BETTER_AUTH_SECRET environment variable matches the secret used by frontend for JWT signing
10. **Database Schema**: Assumes existing 'user' table has 'id' column (text type) for foreign key references

## Out of Scope *(mandatory)*

The following are explicitly NOT included in this feature:

1. **Frontend Development**: ChatKit UI components, React hooks, or Next.js page implementations
2. **User Management**: User registration, login, password reset, or profile management
3. **TODO Backend Modifications**: Any changes to existing REST API endpoints or authentication logic
4. **MCP Server Modifications**: Any changes to existing MCP tools or tool signatures
5. **Voice/Audio Features**: Voice input, audio responses, speech-to-text, or text-to-speech
6. **Multi-modal Support**: Image understanding, file uploads, PDF processing, or document analysis
7. **Advanced Agent Features**: Agent memory beyond conversation history, custom agent personas, or agent switching
8. **Analytics/Monitoring**: Dashboards, usage analytics, performance monitoring, or observability tools
9. **Rate Limiting**: API rate limits, quotas, or throttling mechanisms
10. **Production Infrastructure**: Deployment configurations, load balancers, container orchestration, or CI/CD pipelines
11. **Custom MCP Tools**: Development of new MCP tools beyond the existing 5 task management tools
12. **Thread Management UI**: Thread listing, searching, renaming, or archiving features (basic persistence only)
13. **Export/Import**: Chat history export, import, or backup features
14. **Notifications**: Push notifications, email alerts, or webhooks for chat events
15. **Multi-language Support**: Internationalization, localization, or multi-language responses

## Dependencies *(mandatory)*

### Existing Systems

- **Frontend (Next.js)**: Running on port 3000, provides ChatKit UI and sends authenticated requests
- **TODO Backend API (FastAPI)**: Running on port 9000, handles task CRUD operations via REST
- **TODO MCP Server (Python FastMCP)**: Running on port 3000, exposes 5 task management tools via MCP protocol
- **Neon PostgreSQL**: Cloud-hosted database containing existing user and task tables
- **Better Auth**: JWT-based authentication system generating tokens for frontend requests

### External Services

- **OpenAI API**: Required for GPT-4o-mini model access via OpenAI Agents SDK
  - Account with valid API key
  - Sufficient quota for expected usage
  - Access to GPT-4o-mini model

### Libraries & SDKs

- **FastAPI**: Web framework for building backend API
- **OpenAI Agents Python SDK**: For agent creation and MCP integration
- **ChatKit Python SDK**: For conversation management and streaming
- **python-jose[cryptography]**: For JWT token verification
- **asyncpg or psycopg2**: For PostgreSQL database connectivity
- **python-dotenv**: For environment variable management
- **httpx**: For async HTTP requests to MCP server

### Development Tools

- **Python 3.13+**: Required runtime version
- **UV Package Manager**: Primary package manager for project setup and dependency management
  - Project initialization: `uv init <project-name>`
  - Install dependencies: `uv add <package-name>` (e.g., `uv add openai-agents`, `uv add openai-chatkit`)
  - Run Python files: `uv run <file-name>`
  - Run server: `uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload`
- **Git**: Version control with feature branch workflow
- **Environment variables**: Configuration file (.env) with required secrets

### Package Installation Commands

When setting up the project, use UV to install required packages:

```bash
# Initialize project
uv init chatbot-backend

# Core framework
uv add fastapi
uv add uvicorn[standard]

# OpenAI integrations
uv add openai-agents
uv add openai-chatkit

# Authentication & Security
uv add python-jose[cryptography]
uv add python-dotenv

# Database
uv add asyncpg
uv add sqlmodel

# HTTP client
uv add httpx

# Development/Testing
uv add pytest
uv add pytest-asyncio
```

### Constraints & Requirements

- **Network Connectivity**: Backend must be able to reach:
  - MCP Server at http://localhost:3000
  - OpenAI API endpoints (api.openai.com)
  - Neon PostgreSQL database
- **Database Permissions**: Database user must have:
  - CREATE TABLE permissions for chat_threads and chat_messages
  - SELECT, INSERT, UPDATE, DELETE permissions on created tables
  - Foreign key constraint permissions for CASCADE DELETE
- **Port Availability**: Port 8001 must be available and accessible from frontend
- **Token Compatibility**: JWT tokens must use HS256 algorithm and include 'sub' claim with user_id

## Constraints *(mandatory)*

1. **No MCP Server Modifications**: Must work with existing TODO MCP Server implementation without any code changes to the MCP server
2. **No Authentication Changes**: Must use existing Better Auth JWT token system without modifications to auth flow
3. **Same Database**: Must use existing Neon PostgreSQL database instance (no separate database)
4. **ChatKit Protocol Compliance**: Must follow ChatKit server interface patterns and protocol specifications
5. **Token Security**: Authentication token must never be exposed in agent instructions, logs, or user-visible outputs
6. **Port Assignment**: Backend must run on port 8001 to avoid conflicts with TODO backend (port 9000) and frontend (port 3000)
7. **Response Latency**: Must start streaming response within 3 seconds of receiving request
8. **Stateless Design**: Backend must support concurrent users through stateless request handling (no shared state between requests)
9. **Backward Compatibility**: Must not break existing TODO app functionality or frontend/backend integration
10. **Python Version**: Must use Python 3.13+ (no backward compatibility with older Python versions)
