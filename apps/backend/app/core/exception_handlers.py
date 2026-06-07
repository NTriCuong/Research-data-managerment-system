from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    BadRequestException,
    ConfigurationException,
    ConflictException,
    ExternalServiceException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    PayloadTooLargeException,
    TooManyRequestsException,
    UnauthorizedException,
)


EXCEPTION_STATUS_CODES: dict[type[AppException], int] = {
    BadRequestException: status.HTTP_400_BAD_REQUEST,
    UnauthorizedException: status.HTTP_401_UNAUTHORIZED,
    ForbiddenException: status.HTTP_403_FORBIDDEN,
    NotFoundException: status.HTTP_404_NOT_FOUND,
    ConflictException: status.HTTP_409_CONFLICT,
    PayloadTooLargeException: status.HTTP_413_CONTENT_TOO_LARGE,
    TooManyRequestsException: status.HTTP_429_TOO_MANY_REQUESTS,
    ConfigurationException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    InternalServerException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExternalServiceException: status.HTTP_502_BAD_GATEWAY,
}


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    status_code = next(
        (
            mapped_status
            for exception_type, mapped_status in EXCEPTION_STATUS_CODES.items()
            if isinstance(exc, exception_type)
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )
