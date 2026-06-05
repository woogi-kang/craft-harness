---
name: authorization
description: |
  RBAC (Role-Based Access Control), Scopes, Permissions를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Authorization Skill

RBAC (Role-Based Access Control), Scopes, Permissions를 구현합니다.

## Triggers

- "권한", "authorization", "rbac", "권한 관리", "permission"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `roles` | ❌ | 정의할 역할 목록 |

---

## Output

### Role & Permission 정의

```python
# app/domain/entities/permission.py
from enum import Enum


class Role(str, Enum):
    """User roles."""

    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """Available permissions."""

    # User permissions
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Product permissions
    PRODUCT_READ = "product:read"
    PRODUCT_CREATE = "product:create"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"

    # Order permissions
    ORDER_READ = "order:read"
    ORDER_CREATE = "order:create"
    ORDER_UPDATE = "order:update"
    ORDER_DELETE = "order:delete"

    # Admin permissions
    ADMIN_ACCESS = "admin:access"
    SYSTEM_CONFIG = "system:config"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: set(Permission),  # All permissions
    Role.MANAGER: {
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.PRODUCT_READ,
        Permission.PRODUCT_CREATE,
        Permission.PRODUCT_UPDATE,
        Permission.PRODUCT_DELETE,
        Permission.ORDER_READ,
        Permission.ORDER_UPDATE,
    },
    Role.USER: {
        Permission.USER_READ,
        Permission.PRODUCT_READ,
        Permission.ORDER_READ,
        Permission.ORDER_CREATE,
    },
    Role.GUEST: {
        Permission.PRODUCT_READ,
    },
}


def get_permissions_for_role(role: Role) -> set[Permission]:
    """Get all permissions for a role."""
    return ROLE_PERMISSIONS.get(role, set())


def role_has_permission(role: Role, permission: Permission) -> bool:
    """Check if role has a specific permission."""
    return permission in get_permissions_for_role(role)
```

### User Entity with Role

```python
# app/domain/entities/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.domain.entities.permission import Role


class UserEntity(BaseModel):
    """User domain entity with role."""

    id: int | None = None
    email: EmailStr
    name: str
    hashed_password: str
    role: Role = Role.USER
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role in (Role.ADMIN, Role.MANAGER)
```

### Permission Checker Dependencies

```python
# app/api/v1/dependencies/permissions.py
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.api.v1.dependencies.auth import get_current_active_user
from app.domain.entities.permission import Permission, Role, role_has_permission
from app.domain.entities.user import UserEntity


class PermissionChecker:
    """Dependency class to check user permissions."""

    def __init__(self, required_permissions: list[Permission]) -> None:
        self.required_permissions = required_permissions

    async def __call__(
        self,
        current_user: UserEntity = Depends(get_current_active_user),
    ) -> UserEntity:
        """Check if user has required permissions."""
        for permission in self.required_permissions:
            if not role_has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required",
                )
        return current_user


class RoleChecker:
    """Dependency class to check user roles."""

    def __init__(self, allowed_roles: list[Role]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: UserEntity = Depends(get_current_active_user),
    ) -> UserEntity:
        """Check if user has required role."""
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {[r.value for r in self.allowed_roles]}",
            )
        return current_user


def require_permissions(*permissions: Permission) -> Callable:
    """Dependency factory for permission checking."""
    return PermissionChecker(list(permissions))


def require_roles(*roles: Role) -> Callable:
    """Dependency factory for role checking."""
    return RoleChecker(list(roles))


# Pre-built permission checkers
require_admin = RoleChecker([Role.ADMIN])
require_manager = RoleChecker([Role.ADMIN, Role.MANAGER])
```

### OAuth2 Scopes

```python
# app/api/v1/dependencies/scopes.py
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from app.api.v1.dependencies.services import get_user_service
from app.application.services.user import UserService
from app.core.security import decode_access_token
from app.domain.entities.user import UserEntity

# Define available scopes
SCOPES = {
    "users:read": "Read user information",
    "users:write": "Create and update users",
    "products:read": "Read product information",
    "products:write": "Create and update products",
    "orders:read": "Read order information",
    "orders:write": "Create and update orders",
    "admin": "Full administrative access",
}

oauth2_scheme_scopes = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/form",
    scopes=SCOPES,
)


async def get_current_user_with_scopes(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme_scopes)],
    user_service: UserService = Depends(get_user_service),
) -> UserEntity:
    """Get current user and verify scopes."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    token_scopes = payload.get("scopes", [])

    if user_id is None:
        raise credentials_exception

    user = await user_service.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    # Check required scopes
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required scope: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


# Type alias with scopes
ScopedUser = Annotated[UserEntity, Security(get_current_user_with_scopes)]
```

### 사용 예시

```python
# app/api/v1/routes/users.py
from fastapi import APIRouter, Depends, Security

from app.api.v1.dependencies.permissions import (
    Permission,
    Role,
    require_permissions,
    require_roles,
    require_admin,
)
from app.api.v1.dependencies.scopes import get_current_user_with_scopes
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


# Using permission checker
@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permissions(Permission.USER_READ))],
)
async def list_users(service: UserSvc):
    """List all users (requires USER_READ permission)."""
    return await service.list()


@router.post(
    "",
    response_model=UserResponse,
    dependencies=[Depends(require_permissions(Permission.USER_CREATE))],
)
async def create_user(user_in: UserCreate, service: UserSvc):
    """Create user (requires USER_CREATE permission)."""
    return await service.create(user_in)


# Using role checker
@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_admin)],
)
async def delete_user(user_id: int, service: UserSvc):
    """Delete user (admin only)."""
    return await service.delete(user_id)


# Using OAuth2 scopes
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserEntity = Security(
        get_current_user_with_scopes,
        scopes=["users:read"],
    ),
):
    """Get current user info (requires users:read scope)."""
    return UserResponse.model_validate(current_user)


# Combining multiple permissions
@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    dependencies=[
        Depends(require_roles(Role.ADMIN)),
        Depends(require_permissions(Permission.USER_UPDATE)),
    ],
)
async def update_user_role(
    user_id: int,
    role: Role,
    service: UserSvc,
):
    """Update user role (admin only, requires USER_UPDATE)."""
    return await service.update_role(user_id, role)
```

### Resource-Level Authorization

```python
# app/api/v1/dependencies/ownership.py
from fastapi import Depends, HTTPException, status

from app.api.v1.dependencies.auth import get_current_active_user
from app.domain.entities.user import UserEntity


class OwnershipChecker:
    """Check if user owns the resource or is admin."""

    def __init__(self, get_owner_id: callable) -> None:
        self.get_owner_id = get_owner_id

    async def __call__(
        self,
        resource_id: int,
        current_user: UserEntity = Depends(get_current_active_user),
    ) -> UserEntity:
        owner_id = await self.get_owner_id(resource_id)

        if owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource",
            )

        return current_user


# Usage in routes
async def get_order_owner_id(order_id: int) -> int:
    """Get owner ID of an order."""
    order = await order_service.get_by_id(order_id)
    return order.user_id if order else -1


check_order_ownership = OwnershipChecker(get_order_owner_id)


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    current_user: UserEntity = Depends(check_order_ownership),
):
    """Get order (owner or admin only)."""
    return await order_service.get_by_id(order_id)
```

## References

- `_references/AUTH-PATTERN.md`
