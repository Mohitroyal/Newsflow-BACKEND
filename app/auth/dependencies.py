import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    auto_error=False  # Make it optional so we can handle custom auth errors
)

def _get_or_create_supabase_user(db: Session, supabase_user) -> User:
    """Find existing user by supabase_id or email, or auto-create a new one."""
    if hasattr(supabase_user, '__dict__'):
        data = supabase_user.__dict__
    else:
        data = supabase_user

    supabase_id = data.get("id") or getattr(supabase_user, "id", None)
    email = data.get("email") or getattr(supabase_user, "email", "") or ""
    user_metadata = data.get("user_metadata") or getattr(supabase_user, "user_metadata", {}) or {}

    try:
        # Try by supabase_id first
        if supabase_id:
            user = db.query(User).filter(User.supabase_id == str(supabase_id)).first()
            if user:
                return user

        # Try by email
        if email:
            user = db.query(User).filter(User.email == email).first()
            if user:
                if supabase_id and not user.supabase_id:
                    user.supabase_id = str(supabase_id)
                    db.commit()
                    db.refresh(user)
                return user

        # Auto-create a new user from Supabase profile
        full_name = (
            user_metadata.get("full_name")
            or user_metadata.get("name")
            or (email.split("@")[0] if email else "User")
        )
        new_user = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            supabase_id=str(supabase_id) if supabase_id else None,
            is_active=True,
            is_superuser=False,
            subscription_plan="free",
            subscription_status="active",
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        print(f"[AUTH ERROR] Failed to get or create user, rolling back: {e}")
        raise HTTPException(status_code=500, detail="Database transaction failed during authentication")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    print(f"[AUTH DEBUG] Trying Supabase token (length: {len(token)})")
    try:
        from supabase import create_client
        supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        response = supabase_client.auth.get_user(token)
        if response and response.user:
            return _get_or_create_supabase_user(db, response.user)
    except Exception as e:
        print(f"[AUTH ERROR] Supabase token validation failed: {e}")

    # All paths failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
