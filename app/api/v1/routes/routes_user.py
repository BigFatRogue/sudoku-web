from fastapi import APIRouter, HTTPException, status

from app.db.database import SessionDep

from app.schemas.scheme_users import UserScheme, UserType

from app.repository.repository_auth import AuthRepository
from app.repository.repository_user import UserRepository

from app.models.model_users import ResourcesEnum, ActionEnum

from app.core.enums import TagsEnum, UuidEnum

from ..deps import UserUuidDep


users_router = APIRouter(prefix='/users', tags=[TagsEnum.users])


@users_router.post(
        path='/me', 
        summary='Получение информации о текущем пользователе')
async def check_auth(user_uuid: UserUuidDep, session: SessionDep) -> UserScheme:
    if user_uuid.type == UuidEnum.guest_uuid:
        user = await AuthRepository.get_user_form_guest_uuid(guest_uuid=user_uuid.uuid, session=session)
        return UserScheme(user_id=user.user_id)
    else:
        user = await AuthRepository.get_user_from_session_uuid(session_uuid=user_uuid.uuid, session=session)
        return UserScheme(user_id=user.user_id, username=user.email.split('@')[0], type_user=UserType.user)


@users_router.delete(
    path='/{user_id}', 
    summary='Удаление пользователя')
async def delete_user(user_id: int, user_uuid: UserUuidDep, session: SessionDep) -> dict[str, str | bool]:
    if user_uuid.type == UuidEnum.guest_uuid:
        user = await AuthRepository.get_user_form_guest_uuid(guest_uuid=user_uuid.uuid, session=session)
    else:
        user = await AuthRepository.get_user_from_session_uuid(session_uuid=user_uuid.uuid, session=session)
    
    has_permission = await UserRepository.has_permission(user=user, session=session, resource=ResourcesEnum.user, action=ActionEnum.delete)
    
    if has_permission:
        is_diactivated = await UserRepository.set_active(user_id=user_id, is_active=False, session=session)
        if is_diactivated:
            return {'succses': is_diactivated, 'detail': f'Пользователь {user_id} был удалён'}
        return {'succses': is_diactivated, 'detail': f'Не удалось удалить пользователя {user_id}'}
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')


@users_router.patch(
    path='/{user_id}', 
    summary='Изменения статуса активности пользователя')
async def delete_user(user_id: int, is_active: bool, user_uuid: UserUuidDep, session: SessionDep) -> dict[str, str | bool]:
    if user_uuid.type == UuidEnum.guest_uuid:
        user = await AuthRepository.get_user_form_guest_uuid(guest_uuid=user_uuid.uuid, session=session)
    else:
        user = await AuthRepository.get_user_from_session_uuid(session_uuid=user_uuid.uuid, session=session)
    
    has_permission = await UserRepository.has_permission(user=user, session=session, resource=ResourcesEnum.user, action=ActionEnum.delete)
    
    if has_permission:
        is_diactivated = await UserRepository.set_active(user_id=user_id, is_active=is_active, session=session)
        if is_diactivated:
            return {'succses': is_diactivated, 'detail': f'Пользователь {user_id} был восстановлен'}
        return {'succses': is_diactivated, 'detail': f'Не удалось восстановить пользователя {user_id}'}
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')