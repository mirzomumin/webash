from typing import Any, Dict
from fastapi import HTTPException, status
from docker.errors import ContainerError


class ObjectNotFound(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: Any = "Object does not exist.",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class ObjectAlreadyExists(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_409_CONFLICT,
        detail: Any = "Object already exists.",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class InvalidMediaType(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail: Any = "Invalid media file type",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class CodeInvalidOrExpired(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = "Invalid or expired code",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class TokenInvalid(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: Any = "Token Invalid",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class TokenExpired(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: Any = "Token Expired",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class ContainerUnavailable(HTTPException, ContainerError):
    def __init__(
        self,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        detail: Any = "Container Unavailable",
        headers: Dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
