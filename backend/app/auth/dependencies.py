from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.supabase import get_supabase

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    token = credentials.credentials
    try:
        client = get_supabase()
        response = client.auth.get_user(token)
        if response.user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {"id": str(response.user.id), "email": response.user.email, "access_token": token}
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
