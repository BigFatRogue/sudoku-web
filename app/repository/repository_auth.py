from sqlalchemy import select, delete
import random
from passlib.context import CryptContext

from app.db.database import SessionDep

from app.models.model_users import UserModel, Role, RoleEnum, SessionUserModel, SudokuSolutionUserModel
from app.models.model_sudoku import SudokuModel

from app.schemas.scheme_users import UserRegestartionScheme

from app.core.enums import UuidEnum


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthRepository:
    @classmethod
    async def get_user(cls, uuid: str | None, type_uuid: str, session: SessionDep) -> UserModel | None:
        if not uuid:
            return
        
        if type_uuid == UuidEnum.guest_uuid:
            user = await AuthRepository.get_user_form_guest_uuid(guest_uuid=uuid, session=session)
            return user
    
        else:
            user = await AuthRepository.get_user_from_session_uuid(session_uuid=uuid, session=session)
            return user

    @classmethod
    async def get_user_from_session_uuid(cls, session_uuid: str, session: SessionDep) -> UserModel | None:
        """
        Получения модели пользователя из session_uuid
        """
        result = await session.execute(
            select(UserModel)
            .join(SessionUserModel)
            .where(SessionUserModel.session_uuid == session_uuid)
        )
        
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user 


    @classmethod
    async def get_user_form_guest_uuid(cls, guest_uuid: str, session: SessionDep) -> UserModel | None:
        query = select(UserModel).where(UserModel.uuid==guest_uuid)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user 

    @classmethod
    async def create_guest(cls, guest_uuid: str, session: SessionDep) -> UserModel:
        """
        Создание аккаунта для гостя
        """   
        guest_role_id = await session.execute(select(Role.role_id).where(Role.name == RoleEnum.guest))
        guest = UserModel(uuid=guest_uuid, role_id=guest_role_id.one()[0])
        
        session.add(guest)
        await session.commit()
        await session.refresh(guest)
        
        result_sudoku = await session.execute(select(SudokuModel.sudoku_id, SudokuModel.sudoku))
        sudoku_id, sudoku = random.choice(result_sudoku.all())

        solution_user = SudokuSolutionUserModel(
            user_id=guest.user_id,
            sudoku_id=sudoku_id,
            solution_user=sudoku,
            is_active=True
        )

        session.add(solution_user)
        await session.commit()

        return guest

    @classmethod
    async def create_user_session(cls, user_id: int, session_uuid: str, session: SessionDep) -> None:
        """
        Авторизация пользователя
        """

        session_user = SessionUserModel(
            user_id=user_id,
            session_uuid=session_uuid
        )

        session.add(session_user)
        await session.commit()

    @classmethod
    async def get_user_from_email(cls, user_email: str, session: SessionDep) -> UserModel | None:
        """
        Получения модели пользователя через email
        """

        query = select(UserModel).where(UserModel.email == user_email)
        result = await session.execute(query)

        return result.scalar_one_or_none()

    @classmethod
    async def add_user(cls, guest_uuid: str, user_form: UserRegestartionScheme, session: SessionDep) -> UserModel:
        """
        Создание нового пользователя при регистрации. Перенос данных из guest_uuid в session_uuid
        """
        user = await cls.get_user_form_guest_uuid(guest_uuid, session=session)
        user.email = user_form.email
        user.password = pwd_context.hash(user_form.password)
        user.uuid = None
            
        session.add(user)
        await session.commit()
        await session.refresh(user)
            
        return user

    @classmethod
    async def logout(cls, session_uuid: str, session: SessionDep) -> bool:
        """
        Выход пользователя из сессии. Удаление сессии из SessionUserModel
        """
        try:
            await session.execute(delete(SessionUserModel).where(SessionUserModel.session_uuid == session_uuid))
            session.commit()
            return True
        except Exception:
            return False