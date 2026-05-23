from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from typing import Any

from app.models.user import User
from app.auth.dependencies import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=dict)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user based on verified Supabase JWT
    """
    return jsonable_encoder({
        "success": True,
        "data": current_user,
        "message": "User retrieved successfully"
    })
