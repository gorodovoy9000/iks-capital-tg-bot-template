import logging
from typing import Any

from starlette.datastructures import FormData
from starlette.requests import Request
from starlette_admin import (
    BooleanField,
    DateTimeField,
    IntegerField,
    StringField,
)
from starlette_admin.actions import row_action
from starlette_admin.contrib.sqla.ext.pydantic import ModelView
from starlette_admin.exceptions import ActionFailed

from app.models.sql.user import AdminUser
from app.utils.auth import generate_password_and_hash

logger: logging.Logger = logging.getLogger(__name__)


class AdminUserView(ModelView):
    fields = [
        IntegerField(
            name="user_id",
            label="ID",
            exclude_from_edit=True,
        ),
        DateTimeField(
            name="created_at",
            label="Created at",
            exclude_from_create=True,
            exclude_from_edit=True,
        ),
        StringField(
            name="name",
            label="Name",
        ),
        StringField(
            name="username",
            label="Username",
            exclude_from_edit=True,
        ),
        BooleanField(
            name="is_blocked",
            label="Is blocked",
        ),
        BooleanField(
            name="is_superadmin",
            label="Is superadmin",
        ),
    ]

    async def before_create(self, request: Request, data, admin_user: AdminUser):
        password, password_hash = generate_password_and_hash()
        admin_user.password = password_hash

    async def create(self, *args, **kwargs):
        obj = await super().create(*args, **kwargs)
        print("create", obj)
        return obj

    async def after_create(self, request: Request, obj):
        print("after_create obj", obj)


    def can_create(self, request: Request) -> bool:
        return request.state.user.is_superadmin

    def can_edit(self, request: Request) -> bool:
        return request.state.user.is_superadmin

    def can_delete(self, request: Request) -> bool:
        return request.state.user.is_superadmin

    def can_reset_password(self, request: Request) -> bool:
        return request.state.user.is_superadmin

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        """Added check for reset password row_action."""
        if name == "delete":
            return self.can_delete(request)
        if name == "edit":
            return self.can_edit(request)
        if name == "view":
            return self.can_view_details(request)
        if name == "reset_password":
            return self.can_reset_password(request)
        return True

    @row_action(
        name="reset_password",
        text="Reset user password",
        confirmation="Reset user password?",
        icon_class="fas fa-check-circle",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
        action_btn_class="btn-info",
        form="""
        <form>
            <div class="mt-3">
                <input type="text" class="form-control" name="new-password" placeholder="Enter new password">
            </div>
        </form>
        """,
    )
    async def reset_password_row_action(self, request: Request, pk: Any) -> str:
        # get data from request
        data: FormData = await request.form()
        user_id = int(pk)
        new_password = data.get("new-password")

        # check user is superadmin
        if not request.state.user.is_superadmin:
            raise ActionFailed("Only superadmins can reset passwords")

        # validate new password
        if len(new_password) < 8:
            raise ActionFailed("Password must be at least 8 characters")

        # get target user service and data
        admin_user_service = request.state.admin_user_service
        user = await admin_user_service.get_by_user_id(user_id)
        username = user.username

        # update user password
        await admin_user_service.update_password(username=username, new_password=new_password)

        return f"User '{username}' new password is '{new_password}'"
