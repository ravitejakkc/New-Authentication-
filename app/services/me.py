from app.schemas.auth import UserResponse


def get_jwt_user(current_user: dict) -> UserResponse:
    return UserResponse(
        id=current_user.get("sub"),
        email=current_user.get("email"),
        role=current_user.get("role"),
    )
