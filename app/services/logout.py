from app.schemas.auth import MessageResponse


def logout_jwt(current_user: dict) -> MessageResponse:
    """
    JWT Logout Service.

    Since JWT is stateless, there is no server-side session to delete.
    The client is responsible for discarding the access and refresh tokens.

    This endpoint confirms the logout action by returning a success message.

    NOTE: For production-grade logout with token invalidation,
    implement a token blacklist (e.g. store revoked token JTIs in Redis or DB).
    """
    email = current_user.get("email", "user")
    return MessageResponse(message=f"Logout successful. Goodbye, {email}!")
