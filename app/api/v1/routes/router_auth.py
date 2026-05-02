from fastapi import APIRouter, Request, Response, Form, HTTPException, status
from typing import Annotated
from passlib.context import CryptContext

from app.db.database import SessionDep

from app.schemas.scheme_users import UserAuthScheme, UserRegestartionScheme, UserScheme, UserType

from app.repository.repository_auth import AuthRepository
from app.repository.repository_sudoku import SudokuRepository

from app.core.enums import TagsEnum, UuidEnum

from app.services.cookies import create_uuid_cookie, delete_cookie

from ..deps import UserUuidDep 


auth_router = APIRouter(prefix='/auth', tags=[TagsEnum.auth])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


@auth_router.post(
        path='/user',
        summary='Проверка и присвоение статуса пользователя',
        description='Создание нового пользователя или возврат существующего'
        )
async def get_user(user_uuid: UserUuidDep, response: Response, session: SessionDep) -> UserScheme:
    if user_uuid is None:
        guest_uuid = create_uuid_cookie(UuidEnum.guest_uuid, response=response)
        user = await AuthRepository.create_guest(guest_uuid=guest_uuid, session=session)
        if user:
            return UserScheme(user_id=user.user_id)
    
    user = await AuthRepository.get_user(uuid=user_uuid.uuid, type_uuid=user_uuid.type, session=session)
    if user:
        if user_uuid.type == UuidEnum.session_uuid:
            username = user.email.split('@')[0]
            type_user = UuidEnum.session_uuid
        else:
            username = None
            type_user = UuidEnum.guest_uuid
        return UserScheme(user_id=user.user_id, username=username, type_user=type_user)
    else:
        delete_cookie(UuidEnum.guest_uuid, response=response)
        delete_cookie(UuidEnum.session_uuid, response=response)
        guest_uuid = create_uuid_cookie(UuidEnum.guest_uuid, response=response)
        user = await AuthRepository.create_guest(guest_uuid=guest_uuid, session=session)
        if user:
            return UserScheme(user_id=user.user_id)
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибка в запросе БД')
   

@auth_router.post(
        path='/auth',
        summary='Авторизация по email и password'
        )
async def auth(user_form: Annotated[UserAuthScheme, Form()], session: SessionDep, response: Response) -> UserScheme:
    user = await AuthRepository.get_user_from_email(user_form.email, session=session)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователя не существует')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь был удалён')

    if not pwd_context.verify(user_form.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверный пароль')
    
    session_uuid = create_uuid_cookie(UuidEnum.session_uuid, response=response)

    # Если пользователь зашёл впервый раз
    delete_cookie(UuidEnum.guest_uuid, response=response)
    
    await AuthRepository.create_user_session(user_id=user.user_id, session_uuid=session_uuid, session=session)
    
    return UserScheme(user_id=user.user_id, username=user.email.split('@')[0], type_user=UserType.user)


@auth_router.post(
        path='/registration',
        summary='Регистрация'
        )
async def registration(
    user_uuid: UserUuidDep, 
    user_form: Annotated[UserRegestartionScheme, Form()], 
    session: SessionDep,  
    response: Response
    ) -> UserScheme:

    user = await AuthRepository.get_user_from_email(user_email=user_form.email, session=session)
        
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Пользователь уже существует')

    password = user_form.model_dump().get('password')
    password_repet = user_form.model_dump().get('password_repet')

    if password and password_repet and password != password_repet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Пароль должны совпадать')

    if user_uuid is None or user_uuid.type == UuidEnum.session_uuid:
        delete_cookie(UuidEnum.session_uuid, response=response)
        guest_uuid = create_uuid_cookie(UuidEnum.guest_uuid, response=response)
        await AuthRepository.create_guest(guest_uuid=guest_uuid, session=session)
        delete_cookie(UuidEnum.guest_uuid, response=response)
        
        session_uuid = create_uuid_cookie(UuidEnum.session_uuid, response=response)
        user = await AuthRepository.add_user(guest_uuid=guest_uuid, user_form=user_form, session=session)
        
        await AuthRepository.create_user_session(user_id=user.user_id, session_uuid=session_uuid, session=session) 
    
    else:
        user = await AuthRepository.add_user(guest_uuid=user_uuid.uuid, user_form=user_form, session=session)
        delete_cookie(UuidEnum.guest_uuid, response=response)
        session_uuid = create_uuid_cookie(UuidEnum.session_uuid, response=response)
        await AuthRepository.create_user_session(user_id=user.user_id, session_uuid=session_uuid, session=session)
        
    return UserScheme(user_id=user.user_id, username=user.email.split('@')[0], type_user=UserType.user)


@auth_router.post(
        path='/logout',
        summary='Выход авторизованного пользователя'
        )
async def loguot(user_uuid: UserUuidDep, response: Response, session: SessionDep) -> dict[str, bool]:
    if user_uuid is None or user_uuid.type != UuidEnum.session_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    is_session_del = await AuthRepository.logout(session_uuid=user_uuid.uuid, session=session)
    if is_session_del:
        delete_cookie(UuidEnum.session_uuid, response=response)
    return {'succses': True}