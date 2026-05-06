from fastapi import APIRouter, HTTPException

from app.schemas.auth import AuthLoginInput, AuthLoginOutput, InternalUser
from app.services.auth_service import (
    AUTH_INVALID_CREDENTIALS_MESSAGE,
    AuthError,
    authenticate_internal_user,
    list_safe_internal_users,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=AuthLoginOutput)
def login_internal_user(input_data: AuthLoginInput) -> AuthLoginOutput:
    try:
        return authenticate_internal_user(input_data.username, input_data.password)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=AUTH_INVALID_CREDENTIALS_MESSAGE) from exc


@router.get("/safe-users", response_model=list[InternalUser])
def get_internal_safe_users() -> list[InternalUser]:
    return list_safe_internal_users()
