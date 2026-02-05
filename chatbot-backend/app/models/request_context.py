"""Request context dataclass for per-request authentication and configuration.

This module defines the RequestContext used throughout the ChatKit and Agent execution
to provide user identification and access to the original request.
"""

from dataclasses import dataclass
from fastapi import Request


@dataclass
class RequestContext:
    """Per-request authentication and configuration context.

    This context is created after JWT verification and passed through
    ChatKit server, Store operations, and Agent execution.

    Attributes:
        user_id: Extracted from JWT 'sub' claim for user isolation
        token: Full Authorization header value (format: "Bearer <token>")
        request: FastAPI Request object for additional context
    """

    user_id: str
    token: str
    request: Request
