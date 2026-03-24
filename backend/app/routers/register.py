from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import RegisterRequest, UserRead, UserCreate
from app.core.auth import UserManager, get_user_manager

from app.core.config import settings


# Custom Registration router
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def register_with_code(
        request: RegisterRequest,
        user_manager: UserManager = Depends(get_user_manager)
):
    if request.registration_code != settings.registration_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid registration code"
        )
    
    # Create user
    user = await user_manager.create(
        UserCreate(
            email=request.email,
            password=request.password
        )
    )
    
    return UserRead.model_validate(user)
