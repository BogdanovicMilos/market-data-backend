import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


load_dotenv()


async def token_auth_middleware(
    request: Request,
    auth: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> Request:
    """Simple Bearer token check against a hard-coded value."""
    token = os.getenv("VALID_BEARER_TOKEN")

    if not auth or auth.credentials != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.token = auth.credentials
    return request
