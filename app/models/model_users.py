from sqlalchemy import ForeignKey, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import StrEnum

from app.db.database import Model


class RoleEnum(StrEnum):
    guest: str = 'guest'
    user: str = 'user'
    admin: str = 'admin'


class ActionEnum(StrEnum):
    create: str = 'create'
    read: str = 'read'
    update: str = 'update'
    delete: str = 'delete'


class ResourcesEnum(StrEnum):
    user: str = 'user'
    sudoku: str = 'sudoku'


class Role(Model):
    __tablename__ = 'role'
    role_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[RoleEnum] = mapped_column(unique=True, nullable=False)

    user: Mapped['UserModel'] = relationship(back_populates='role', init=False)
    role_permission: Mapped['RolePermissionModel'] = relationship(back_populates='role', init=False)


class PermissionModel(Model):
    __tablename__ = "permissions"
    permission_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    resources: Mapped[ResourcesEnum] = mapped_column(nullable=False)
    action: Mapped[ActionEnum] = mapped_column(nullable=False)

    role_permission: Mapped['RolePermissionModel'] = relationship(back_populates='permission', init=False)

    __table_args__ = (UniqueConstraint('resources', 'action', name='uq_resource_action'),)


class RolePermissionModel(Model):
    __tablename__ = "role_permissions"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('role.role_id'), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey('permissions.permission_id'), nullable=False)

    role: Mapped['Role'] = relationship(back_populates='role_permission', init=False)
    permission: Mapped['PermissionModel'] = relationship(back_populates='role_permission', init=False)


class UserModel(Model):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('role.role_id'), nullable=False)
    uuid: Mapped[str | None] = mapped_column(default=None, unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(default=None, unique=True, nullable=True)
    password: Mapped[str | None] = mapped_column(default=None, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    create_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), init=False)
    
    role: Mapped['Role'] = relationship(back_populates='user', init=False)
    solutions: Mapped[list['SudokuSolutionUserModel']] = relationship(back_populates='user', cascade="all", init=False)
    session_user: Mapped['SessionUserModel'] = relationship(back_populates='user', cascade="all", init=False)


class SessionUserModel(Model):
    __tablename__ = 'session_user'

    session_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete="CASCADE"))
    session_uuid: Mapped[str] = mapped_column(unique=True)
    create_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), init=False)

    user: Mapped['UserModel'] = relationship(back_populates='session_user', init=False)


class SudokuSolutionUserModel(Model):
    __tablename__ = 'sudoku_solved_user'

    user_solution_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete="CASCADE"))
    sudoku_id: Mapped[int]
    solution_user: Mapped[str]
    user: Mapped['UserModel'] = relationship(back_populates='solutions', init=False)

    solving_time: Mapped[int] = mapped_column(default=0) # В секундах
    is_solved: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)

    
    def __repr__(self):
        return f'({self.user_solution_id}, {self.user_id}, {self.sudoku_id}, {self.solution_user}, {self.solving_time}, {self.is_solved}, {self.is_active})'
    
    def __str__(self):
        return self.__repr__()