from typing import Annotated

from pydantic import BaseModel, Field


class InAdminUser(BaseModel):
    name: Annotated[str, Field(min_length=4, max_length=30)] = None
    username: Annotated[str, Field(min_length=4, max_length=30)] = None
