"""Better Auth session token verification.

This module provides FastAPI dependency injection for Better Auth session authentication.
Tokens are verified against the database session table (not JWT).
"""

from fastapi import Header, HTTPException
from typing import Annotated
from datetime import datetime
import logging
import asyncpg

from app.config import settings

logger = logging.getLogger(__name__)


async def verify_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract and verify Better Auth session token from database.

    Args:
        authorization: Authorization header value (format: "Bearer <token>")

    Returns:
        user_id: Extracted from database session table

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing authorization token"
        )

    token = authorization.removeprefix("Bearer ")

    logger.info(f"Verifying session token: {token[:20]}...")

    try:
        # Connect to database using asyncpg
        conn = await asyncpg.connect(settings.database_url.replace('+asyncpg', ''))

        try:
            # Query Better Auth session table
            result = await conn.fetchrow(
                """
                SELECT "userId", "expiresAt"
                FROM session
                WHERE token = $1
                """,
                token
            )

            if not result:
                logger.warning("Invalid token: not found in database")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token"
                )

            user_id = result['userId']
            expires_at = result['expiresAt']

            # Check if session is expired
            if expires_at:
                # Handle timezone-aware comparison
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))

                # Compare with current UTC time
                now = datetime.utcnow()
                exp_time = expires_at.replace(tzinfo=None) if expires_at.tzinfo else expires_at

                if now > exp_time:
                    logger.warning(f"Token expired: {expires_at}")
                    raise HTTPException(
                        status_code=401,
                        detail="Session expired"
                    )

            logger.info(f"Token verified successfully for user: {user_id}")
            return user_id

        finally:
            await conn.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session verification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
