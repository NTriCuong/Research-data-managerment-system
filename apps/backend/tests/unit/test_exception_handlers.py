import json

import pytest
from fastapi import status

from app.core.exception_handlers import app_exception_handler
from app.core.exceptions import (
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exception_type", "expected_status"),
    [
        (BadRequestException, status.HTTP_400_BAD_REQUEST),
        (UnauthorizedException, status.HTTP_401_UNAUTHORIZED),
        (ForbiddenException, status.HTTP_403_FORBIDDEN),
        (NotFoundException, status.HTTP_404_NOT_FOUND),
        (ConflictException, status.HTTP_409_CONFLICT),
        (PayloadTooLargeException, status.HTTP_413_CONTENT_TOO_LARGE),
        (TooManyRequestsException, status.HTTP_429_TOO_MANY_REQUESTS),
        (ConfigurationException, status.HTTP_500_INTERNAL_SERVER_ERROR),
        (InternalServerException, status.HTTP_500_INTERNAL_SERVER_ERROR),
        (ExternalServiceException, status.HTTP_502_BAD_GATEWAY),
    ],
)
async def test_app_exception_handler_maps_status_and_detail(exception_type, expected_status):
    response = await app_exception_handler(None, exception_type("test detail"))

    assert response.status_code == expected_status
    assert json.loads(response.body) == {"detail": "test detail"}


@pytest.mark.asyncio
async def test_app_exception_handler_preserves_headers():
    response = await app_exception_handler(
        None,
        UnauthorizedException("invalid token", headers={"WWW-Authenticate": "Bearer"}),
    )

    assert response.headers["www-authenticate"] == "Bearer"
