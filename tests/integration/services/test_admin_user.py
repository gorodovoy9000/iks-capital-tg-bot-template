import pytest

from app.models.sql import AdminUser
from app.services.user import AdminUserService


class TestAdminUserService:
    """Тесты для работы с админами."""

    @pytest.mark.asyncio
    async def test_get_admin_user_by_tg_id(self, test_admin_user: AdminUser, admin_user_service: AdminUserService):
        """Тест получения админа по user_id."""
        # написал для того что там добавил
        admin_user = await admin_user_service.get_by_user_id(test_admin_user.user_id)

        assert admin_user is not None
        assert admin_user.user_id == test_admin_user.user_id
        assert admin_user.name == "Admin1"
        assert admin_user.username == "admin_user1"
        assert admin_user.is_blocked is False
        assert admin_user.is_superadmin is False
