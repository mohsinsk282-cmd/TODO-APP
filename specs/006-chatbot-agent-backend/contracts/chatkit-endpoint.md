# API Contract: ChatKit Endpoint

**Feature**: 006-chatbot-agent-backend
**Endpoint**: POST /api/chatkit
**Protocol**: ChatKit Protocol (OpenAI specification)
**Date**: 2026-02-02

---

## Overview

Single endpoint that handles all ChatKit protocol operations including:
- Creating new threads
- Loading thread history
- Sending user messages
- Streaming assistant responses
- Thread metadata operations

All protocol handling is delegated to `ChatKitServer.process()` method (FR-029).

---

## Endpoint Specification

**HTTP Method**: POST

**URL**: `/api/chatkit`

**Content-Type**: `application/json`

**Authentication**: Required - Better Auth JWT token in Authorization header

---

## Request Format

### Headers

```http
POST /api/chatkit HTTP/1.1
Host: localhost:8001
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Required Headers**:
- `Authorization`: Bearer token (HS256 JWT from Better Auth)
- `Content-Type`: application/json

### Body (ChatKit Protocol)

ChatKit protocol messages follow this general structure:

```json
{
  "type": "create_thread" | "get_thread" | "send_message" | "list_threads",
  "data": {
    // Operation-specific payload
  }
}
```

**Example: Send User Message (Streaming)**

```json
{
  "type": "send_message",
  "data": {
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": {
      "role": "user",
      "content": "Show me my incomplete tasks"
    },
    "stream": true
  }
}
```

**Example: Create New Thread**

```json
{
  "type": "create_thread",
  "data": {
    "title": "Task Planning Discussion"
  }
}
```

**Example: Get Thread History**

```json
{
  "type": "get_thread",
  "data": {
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "limit": 20,
    "order": "asc"
  }
}
```

---

## Response Formats

### Success - Streaming Response (SSE)

**Status**: 200 OK

**Content-Type**: `text/event-stream`

**Body**: Server-Sent Events (SSE) stream with ChatKit ThreadStreamEvent objects

```
event: thread_item_delta
data: {"type":"thread_item_delta","item_id":"msg_123","delta":{"content":[{"type":"text","text":"You"}]}}

event: thread_item_delta
data: {"type":"thread_item_delta","item_id":"msg_123","delta":{"content":[{"type":"text","text":" have"}]}}

event: thread_item_delta
data: {"type":"thread_item_delta","item_id":"msg_123","delta":{"content":[{"type":"text","text":" 3"}]}}

event: thread_item_done
data: {"type":"thread_item_done","item":{"id":"msg_123","thread_id":"550e...","role":"assistant","content":[{"type":"text","text":"You have 3 incomplete tasks..."}],"created_at":"2026-02-02T10:00:05Z"}}

event: done
data: {"type":"done"}
```

**Event Types**:
- `thread_item_delta`: Incremental content updates (token-by-token streaming)
- `thread_item_done`: Complete message when finished
- `agent_updated_stream_event`: Agent handoff notifications
- `run_item_stream_event`: Tool call notifications
- `done`: End of stream

### Success - Non-Streaming Response (JSON)

**Status**: 200 OK

**Content-Type**: `application/json`

```json
{
  "type": "thread_created",
  "data": {
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-02-02T10:00:00Z"
  }
}
```

Or for thread retrieval:

```json
{
  "type": "thread",
  "data": {
    "thread": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Task Planning Discussion",
      "created_at": "2026-02-02T10:00:00Z",
      "updated_at": "2026-02-02T10:05:30Z"
    },
    "messages": [
      {
        "id": "msg_1",
        "role": "user",
        "content": [{"type": "text", "text": "Show me my tasks"}],
        "created_at": "2026-02-02T10:00:00Z"
      },
      {
        "id": "msg_2",
        "role": "assistant",
        "content": [{"type": "text", "text": "You have 3 tasks..."}],
        "created_at": "2026-02-02T10:00:05Z"
      }
    ],
    "has_more": false
  }
}
```

---

## Error Responses

### 401 Unauthorized

**When**: Missing, invalid, or expired JWT token

```json
{
  "error": {
    "type": "authentication_error",
    "message": "Invalid or expired token",
    "status_code": 401
  }
}
```

### 404 Not Found

**When**: Thread doesn't exist or doesn't belong to authenticated user

```json
{
  "error": {
    "type": "not_found_error",
    "message": "Thread not found",
    "status_code": 404,
    "thread_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 503 Service Unavailable

**When**: OpenAI API or MCP server temporarily unavailable

```json
{
  "error": {
    "type": "agent_error",
    "message": "Assistant is temporarily unavailable. Please try again.",
    "status_code": 503,
    "request_id": "req_abc123"
  }
}
```

Or for MCP server errors:

```json
{
  "error": {
    "type": "mcp_error",
    "message": "Task management features are temporarily unavailable.",
    "status_code": 503,
    "request_id": "req_abc123"
  }
}
```

### 500 Internal Server Error

**When**: Unexpected backend error

```json
{
  "error": {
    "type": "internal_error",
    "message": "An unexpected error occurred. Please try again.",
    "status_code": 500,
    "request_id": "req_abc123"
  }
}
```

---

## Implementation

### FastAPI Endpoint Handler

```python
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from chatkit.server import StreamingResult
from typing import Annotated
import logging

app = FastAPI(title="Chatbot Backend")
logger = logging.getLogger(__name__)

@app.post("/api/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: Annotated[str, Depends(verify_token)]
) -> Response:
    """
    ChatKit protocol endpoint - handles all conversation operations.

    Delegates protocol handling to ChatKitServer.process() which:
    - Parses ChatKit protocol messages
    - Routes to appropriate Store methods
    - Invokes custom respond() for user messages
    - Returns streaming or static responses

    Args:
        request: FastAPI Request object with ChatKit protocol body
        user_id: Extracted from JWT via dependency injection

    Returns:
        StreamingResponse for streaming operations (SSE)
        Response for static operations (JSON)

    Raises:
        HTTPException(401): Authentication failure
        HTTPException(404): Thread not found or unauthorized
        HTTPException(503): External service unavailable
        HTTPException(500): Internal server error
    """
    try:
        # Create request context with auth info
        context = RequestContext(
            user_id=user_id,
            token=request.headers["authorization"],
            request=request
        )

        # Log request (without sensitive data)
        request_id = str(uuid.uuid4())
        logger.info(
            f"ChatKit request",
            extra={"request_id": request_id, "user_id": user_id}
        )

        # Delegate to ChatKit server
        result = await chatkit_server.process(await request.body(), context)

        # Return appropriate response type
        if isinstance(result, StreamingResult):
            logger.info(f"Streaming response", extra={"request_id": request_id})
            return StreamingResponse(result, media_type="text/event-stream")
        else:
            logger.info(f"Static response", extra={"request_id": request_id})
            return Response(content=result.json, media_type="application/json")

    except NotFoundError as e:
        logger.warning(f"Thread not found: {e}", extra={"user_id": user_id})
        raise HTTPException(status_code=404, detail=str(e))

    except AgentError as e:
        logger.error(f"Agent error: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=503, detail=str(e))

    except MCPError as e:
        logger.error(f"MCP error: {e}", extra={"request_id": request_id})
        raise HTTPException(status_code=503, detail=str(e))

    except Exception as e:
        logger.exception(f"Unexpected error: {e}", extra={"request_id": request_id})
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )
```

---

## Authentication Flow

```
1. Frontend sends request with Authorization: Bearer <jwt>
   ↓
2. verify_token() dependency extracts and validates JWT
   - Decodes with BETTER_AUTH_SECRET
   - Verifies HS256 signature
   - Extracts user_id from 'sub' claim
   ↓
3. If invalid/missing → HTTPException(401)
   ↓
4. If valid → user_id passed to endpoint handler
   ↓
5. RequestContext created with user_id and token
   ↓
6. Context passed to ChatKitServer.process()
   ↓
7. Store methods filter by context.user_id (data isolation)
   ↓
8. Agent created with context.token in MCP headers
```

---

## Performance Characteristics

### Latency Requirements

- **First token** (SC-001): < 3 seconds from request to first SSE event
- **Visible content** (SC-006): < 1 second from agent starting generation to first content_delta

### Concurrency

- **Concurrent users** (SC-005): Supports 10 simultaneous users without degradation
- **Stateless design**: Each request is independent (no shared state)

### Throughput

- **Message persistence**: Async database operations don't block streaming
- **Thread history**: Loading last 20 messages optimized with indexes

---

## Testing Examples

### curl: Send Message (Streaming)

```bash
curl -X POST http://localhost:8001/api/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  --no-buffer \
  -d '{
    "type": "send_message",
    "data": {
      "thread_id": "550e8400-e29b-41d4-a716-446655440000",
      "message": {
        "role": "user",
        "content": "Show me my tasks"
      },
      "stream": true
    }
  }'
```

### Python httpx: Create Thread

```python
import httpx
import json

async def create_thread(token: str, title: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/chatkit",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "type": "create_thread",
                "data": {"title": title}
            },
            timeout=10.0
        )
        return response.json()

# Usage
result = await create_thread(user_token, "My Conversation")
print(f"Thread created: {result['data']['thread_id']}")
```

### Python httpx: Stream Messages

```python
import httpx
import json

async def stream_message(token: str, thread_id: str, message: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8001/api/chatkit",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "type": "send_message",
                "data": {
                    "thread_id": thread_id,
                    "message": {"role": "user", "content": message},
                    "stream": True
                }
            },
            timeout=30.0
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data["type"] == "thread_item_delta":
                        print(data["delta"]["content"][0]["text"], end="", flush=True)
                    elif data["type"] == "done":
                        print()  # New line at end
                        break
```

---

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

## Related Documents

- **Data Model**: [data-model.md](../data-model.md) - ChatThread and ChatMessage schemas
- **Specification**: [spec.md](../spec.md) - Functional requirements FR-026 to FR-029
- **Phase 0 Decisions**: [plan.md](../plan.md#phase-0-research--design-decisions) - Decision 5 (Streaming Response Handling)
