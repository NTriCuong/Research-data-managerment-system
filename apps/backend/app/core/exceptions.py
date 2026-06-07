from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppException(Exception):
    detail: str
    headers: dict[str, str] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        Exception.__init__(self, self.detail)


class BadRequestException(AppException):
    pass


class UnauthorizedException(AppException):
    pass


class ForbiddenException(AppException):
    pass


class NotFoundException(AppException):
    pass


class ConflictException(AppException):
    pass


class PayloadTooLargeException(AppException):
    pass


class TooManyRequestsException(AppException):
    pass


class ConfigurationException(AppException):
    pass


class InternalServerException(AppException):
    pass


class ExternalServiceException(AppException):
    pass


credentials_exception = UnauthorizedException(
    detail="Không thể xác thực thông tin đăng nhập",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_user_exception = ForbiddenException(
    detail="Tài khoản người dùng không hoạt động",
)


def forbidden_exception(detail: str = "Bạn không có đủ quyền để thực hiện thao tác này") -> ForbiddenException:
    return ForbiddenException(detail=detail)
