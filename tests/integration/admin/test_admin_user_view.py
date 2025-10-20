import pytest
from starlette.requests import Request
from starlette_admin._types import RequestAction
from starlette_admin.exceptions import FormValidationError


from app.admin.views.admin_user import AdminUserView
from app.models.sql import AdminUser
from app.services.postgres import Repository


class TestAdminUserService:
    """Тесты для работы с админом."""

    @pytest.mark.asyncio
    async def test_create_edit_admin_user(
            self,
            repository: Repository,
            test_admin_user_view: AdminUserView,
    ):
        # test create admin user
        state = {"action": RequestAction.CREATE, "session": repository.session}
        request = Request({"type": "http", "state": state})

        data = {
            "name": "admin2",
            "username": "admin2",
            "is_blocked": False,
            "is_superadmin": False,
        }

        result: AdminUser = await test_admin_user_view.create(request=request, data=data)
        assert result.username == data["username"]
        assert result.password

        # test update user
        state = {"action": RequestAction.EDIT, "session": repository.session}
        request = Request({"type": "http", "state": state})

        data = {
            "name": "admin2_new",
            "username": "admin2",
            "is_blocked": False,
            "is_superadmin": False,
        }

        result: AdminUser = await test_admin_user_view.edit(request=request, data=data, pk=result.user_id)
        assert result.name == data["name"]

        # delete user
        # Методы create, edit делают session.commit() поэтому удаляем объект
        # Не стал тратить время на мок session.commit()
        state = {"action": RequestAction.ACTION, "session": repository.session}
        request = Request({"type": "http", "state": state})
        result: int = await test_admin_user_view.delete(request=request, pks=[result.user_id])
        assert result == 1


    @pytest.mark.asyncio
    async def test_admin_user_validation(self, test_admin_user_view: AdminUserView):
        # set request with state
        state = {"action": RequestAction.CREATE}
        request = Request({"type": "http", "state": state})
        # check validation fails on small strings
        data = {
            "name": "",
            "username": "",
            "is_blocked": False,
            "is_superadmin": False,
        }
        try:
            await test_admin_user_view.create(request, data)
        except FormValidationError:
            pass
        else:
            assert False
        # check validation fails on big strings
        data = {
            "name": "a"*70,
            "username": "a"*70,
            "is_blocked": False,
            "is_superadmin": False,
        }
        try:
            await test_admin_user_view.create(request, data)
        except FormValidationError:
            pass
        else:
            assert False

    @pytest.mark.asyncio
    async def test_admin_user_security(
            self,
            test_admin_user_view: AdminUserView,
            test_superadmin_user: AdminUser,
            test_admin_user: AdminUser,
            test_blocked_admin_user: AdminUser,
    ):
        # test superadmin can do all
        state = {"user": test_superadmin_user, "action": RequestAction.ACTION}
        request = Request({"type": "http", "state": state})
        assert test_admin_user_view.can_view_details(request)
        assert test_admin_user_view.can_create(request)
        assert test_admin_user_view.can_edit(request)
        assert test_admin_user_view.can_delete(request)
        assert test_admin_user_view.can_reset_password(request)

        # test standard admin can only view
        state = {"user": test_admin_user, "action": RequestAction.ACTION}
        request = Request({"type": "http", "state": state})
        assert test_admin_user_view.can_view_details(request)
        assert not test_admin_user_view.can_create(request)
        assert not test_admin_user_view.can_edit(request)
        assert not test_admin_user_view.can_delete(request)
        assert not test_admin_user_view.can_reset_password(request)

        # test blocked admin cannot do anything
        state = {"user": test_blocked_admin_user, "action": RequestAction.ACTION}
        request = Request({"type": "http", "state": state})
        assert not test_admin_user_view.can_view_details(request)
        assert not test_admin_user_view.can_create(request)
        assert not test_admin_user_view.can_edit(request)
        assert not test_admin_user_view.can_delete(request)
        assert not test_admin_user_view.can_reset_password(request)
