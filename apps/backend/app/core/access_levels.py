from app.models.enum import AccessLevel


ACCESS_LEVEL_RANK = {
    AccessLevel.private: 0,
    AccessLevel.internal: 1,
    AccessLevel.public: 2,
}


def is_access_level_allowed(
    resource_access_level: AccessLevel,
    container_access_level: AccessLevel,
) -> bool:
    """A contained resource cannot be more visible than its container."""
    return ACCESS_LEVEL_RANK[resource_access_level] <= ACCESS_LEVEL_RANK[container_access_level]
