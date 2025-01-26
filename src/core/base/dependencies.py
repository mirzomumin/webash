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
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008)  # Policy Violation
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Not Authorized",
            )
        return token

    if request:
        return await oauth2_scheme(request)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported connection type",
    )
