import os
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import RegisterRequest, UserRead, UserCreate
from app.auth import UserManager, get_user_manager


# Custom Registration router
router = APIRouter(prefix="/auth", tags=["auth"])

REGISTRATION_CODE = os.getenv("REGISTRATION_CODE", "local-code")

@router.post("/register", response_model=UserRead)
async def register_with_code(
        request: RegisterRequest,
        user_manager: UserManager = Depends(get_user_manager)
):
    if request.registration_code != REGISTRATION_CODE:
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
