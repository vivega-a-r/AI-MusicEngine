import hmac
import hashlib
from typing import Optional
from fastapi import Header, HTTPException, Depends
from backend.app.core.config import settings
from backend.app.core.logging import logger

class AuthenticatedUser:
    def __init__(self, user_id: str, email: Optional[str] = None, auth_provider: str = "local_dev"):
        self.user_id = user_id
        self.email = email
        self.auth_provider = auth_provider

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "auth_provider": self.auth_provider
        }

async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> AuthenticatedUser:
    """
    Authenticates requests via Firebase Auth (if configured) or Local Development Auth.
    Clearly marks whether auth was performed via verified Firebase or local dev mode.
    """
    if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_CREDENTIALS_PATH:
        # In a configured Firebase environment, verify the Firebase ID token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Bearer token for Firebase authentication.")
        
        token = authorization.split("Bearer ")[1].strip()
        try:
            # Here we would call firebase_admin.auth.verify_id_token(token)
            # For local dev without cloud credentials, we ensure honesty:
            raise HTTPException(status_code=503, detail="Firebase project credentials not yet connected to Google Cloud.")
        except Exception as e:
            logger.warning(f"Firebase token verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Firebase authentication failed: {str(e)}")

    # Local development mode
    if settings.ENABLE_LOCAL_DEV_AUTH:
        # Default or custom user ID
        user_id = x_user_id or "dev_creator_default"
        if authorization and authorization.startswith("Bearer dev-"):
            user_id = authorization.split("Bearer dev-")[1].strip() or user_id
            
        return AuthenticatedUser(
            user_id=user_id,
            email=f"{user_id}@incubrix.local",
            auth_provider="local_dev_mode"
        )

    raise HTTPException(status_code=401, detail="Authentication credentials required.")

def generate_hmac_signature(payload_bytes: bytes, secret: str = settings.SECRET_KEY) -> str:
    """Generates HMAC-SHA256 signature for webhooks/callbacks."""
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

def verify_hmac_signature(payload_bytes: bytes, signature: str, secret: str = settings.SECRET_KEY) -> bool:
    """Verifies HMAC-SHA256 signature."""
    expected = generate_hmac_signature(payload_bytes, secret)
    return hmac.compare_digest(expected, signature)
