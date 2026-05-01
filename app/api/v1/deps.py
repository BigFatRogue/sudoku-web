from fastapi import Depends, Request
from typing import Annotated

from app.core.context import UserUuidContext
from app.core.enums import UuidEnum

from app.models.model_users import ActionEnum, ResourcesEnum
from app.db.database import SessionDep
from app.repository.repository_auth import AuthRepository
from app.repository.repository_user import UserRepository


def get_user_uuid(request: Request) -> UserUuidContext | None:
    session_uuid = request.cookies.get(UuidEnum.session_uuid)

    if session_uuid:
        return UserUuidContext(session_uuid, UuidEnum.session_uuid)
    else:
        get_user_uuid = request.cookies.get(UuidEnum.guest_uuid)
        if get_user_uuid:
            return UserUuidContext(get_user_uuid, UuidEnum.guest_uuid)
    
    return None

UserUuidDep = Annotated[UserUuidContext, Depends(get_user_uuid)]

