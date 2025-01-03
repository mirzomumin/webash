from fastapi import Request, WebSocket, HTTPException, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_token(
    request: Request = None,
    websocket: WebSocket = None,
) -> str:
    """Get authorization token"""

    if websocket:
        authorization: str = websocket.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Not Authorized",
            )
        return authorization.split("Bearer ")[1]

    if request:
        return await oauth2_scheme(request)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported connection type",
    )
