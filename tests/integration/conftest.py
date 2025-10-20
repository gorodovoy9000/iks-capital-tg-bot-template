from typing import Any, Callable, Coroutine

import pytest_asyncio

from app.admin.views.admin_user import AdminUserView
from app.models.config import AppConfig
from app.models.sql import AdminUser, User
from app.services.postgres import Repository
from app.services.user import AdminUserService, UserService
from app.utils.auth import hash_password
from app.validators.admin_user import InAdminUser


@pytest_asyncio.fixture
async def user_service(
    repository: Repository,
    app_config: AppConfig,
) -> UserService:
    """Создаёт экземпляр UserService."""
    return UserService(repository=repository, config=app_config)


@pytest_asyncio.fixture
async def admin_user_service(
    repository: Repository,
    app_config: AppConfig,
) -> AdminUserService:
    """Создаёт экземпляр AdminUserService."""
    return AdminUserService(repository=repository, config=app_config)


@pytest_asyncio.fixture
async def create_test_user(repository: Repository) -> Callable[[], Coroutine[Any, Any, User]]:
    """Создаёт тестового пользователя с настраиваемыми параметрами."""

    async def _impl(
        telegram_id: int | None = None,
        name: str | None = None,
        username: str | None = None,
        language: str = "ru",
        language_code: str | None = None,
        bot_blocked: bool = False,
    ) -> User:
        """
        Создаёт пользователя с заданными параметрами.
        """

        if telegram_id is None:
            telegram_id = 100000000 + len(repository.session.identity_map)

        if name is None:
            name = f"Test User {telegram_id}"

        user = User(
            telegram_id=telegram_id,
            name=name,
            username=username,
            language=language,
            language_code=language_code,
            bot_blocked=bot_blocked,
        )

        repository.session.add(user)
        await repository.session.flush()
        return user

    return _impl


@pytest_asyncio.fixture
async def create_test_admin_user(repository: Repository) -> Callable[[], Coroutine[Any, Any, AdminUser]]:
    """Создаёт тестового админа с настраиваемыми параметрами."""

    async def _impl(
        username: str,
        password: str,
        name: str | None = None,
        is_blocked: bool = False,
        is_superadmin: bool = False,
    ) -> AdminUser:
        """
        Создаёт админа с заданными параметрами.
        """

        if name is None:
            name = f"Test Admin User {username}"

        # hash password
        password_hash = hash_password(password)

        admin_user = AdminUser(
            name=name,
            username=username,
            password=password_hash,
            is_blocked=is_blocked,
            is_superadmin=is_superadmin,
        )

        repository.session.add(admin_user)
        await repository.session.flush()
        return admin_user

    return _impl


@pytest_asyncio.fixture
async def test_user(repository: Repository, create_test_user) -> User:
    """Создаёт базового тестового пользователя."""
    return await create_test_user(
        telegram_id=123456789,
        name="TestUser",
        username="test_user",
        language="ru",
        language_code="ru",
    )


@pytest_asyncio.fixture
async def test_superadmin_user(repository: Repository, create_test_admin_user) -> AdminUser:
    """Создаёт супер админа."""
    return await create_test_admin_user(
        name="SuperAdmin",
        username="superadmin_user",
        password="superadmin_password",
        is_blocked = False,
        is_superadmin = True,
    )


@pytest_asyncio.fixture
async def test_admin_user(repository: Repository, create_test_admin_user) -> AdminUser:
    """Создаёт обычного админа."""
    return await create_test_admin_user(
        name="Admin1",
        username="admin_user1",
        password="admin_password1",
        is_blocked = False,
        is_superadmin = False,
    )


@pytest_asyncio.fixture
async def test_blocked_admin_user(repository: Repository, create_test_admin_user) -> AdminUser:
    """Создаёт заблокированного админа."""
    return await create_test_admin_user(
        name="AdminB",
        username="admin_userB",
        password="admin_passwordB",
        is_blocked = True,
        is_superadmin = False,
    )


@pytest_asyncio.fixture
async def test_admin_user_view():
    return AdminUserView(AdminUser, pydantic_model=InAdminUser)
