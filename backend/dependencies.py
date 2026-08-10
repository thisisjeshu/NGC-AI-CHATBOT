from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.auth import decode_access_token


security = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    admin = decode_access_token(token)

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )

    if admin.get("role") not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return admin