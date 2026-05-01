import os
import json
import random
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext


if __name__ == '__main__':
    # Для запуска через IDE

    import sys
    test_path = str(Path(__file__).parent.parent.parent)
    print(test_path)
    sys.path.append(test_path)


from app.core.config import settings
from app.models.model_users import (
    ActionEnum, 
    RoleEnum,
    ResourcesEnum,
    Role,
    PermissionModel,
    RolePermissionModel,
    UserModel) 
from app.models.model_sudoku import SudokuModel, SolutionSudokuModel
from app.models.model_users import SudokuSolutionUserModel

def initial_table_sudoku(session: Session) -> bool:
    PATH_DATASETD = str(Path(__file__).parent.parent / 'services/sudoku/dataset.json')
    if os.path.exists(PATH_DATASETD):
        with open(PATH_DATASETD, 'r', encoding='utf-8') as dt:
            dataset: dict[int, list[str]] = json.load(dt)
    else:
        print(f'Файл {PATH_DATASETD} не найден')
        return False

    for quality, sudokus in dataset.items():
        for data in sudokus:
            sudoku, solution = data['sudoku'], data['solution']
            
            sudoku = SudokuModel(quality=quality, sudoku=sudoku)
            solution = SolutionSudokuModel(solution=solution)

            sudoku.solutions.append(solution)

            session.add(sudoku)
    
    return True

def initial_role(session: Session) -> dict[RoleEnum, Role]:
    roles = {}
    for r in RoleEnum:
        role = Role(name=r.value)
        roles[r] = role
        session.add(role)
    session.flush()
    return roles

def init_permision(session: Session) -> dict[tuple[ResourcesEnum, ActionEnum], PermissionModel]:
    permissions = {}
    for resources in ResourcesEnum:
        for action in ActionEnum:
            permition = PermissionModel(resources=resources.value, action=action.value)
            permissions[(resources, action)] = permition
            session.add(permition)
    session.flush()

    return permissions

def initial_role_permission(
        session: Session, 
        roles_db: dict[RoleEnum, Role], 
        permission_db: dict[tuple[ResourcesEnum, ActionEnum], PermissionModel]) -> None:
    # {
    #   role: (
    #       (resources, action), 
    #   )
    # }
    role_permission: dict[RoleEnum, tuple[tuple[ResourcesEnum, ActionEnum]]] = {
        RoleEnum.admin: (
            (ResourcesEnum.user, ActionEnum.create),
            (ResourcesEnum.user, ActionEnum.read),
            (ResourcesEnum.user, ActionEnum.update),
            (ResourcesEnum.user, ActionEnum.delete),
            (ResourcesEnum.sudoku, ActionEnum.create),
            (ResourcesEnum.sudoku, ActionEnum.read),
            (ResourcesEnum.sudoku, ActionEnum.update),
            (ResourcesEnum.sudoku, ActionEnum.delete)
        ),
        RoleEnum.user: (
            (ResourcesEnum.user, ActionEnum.read),
            (ResourcesEnum.user, ActionEnum.update),
            (ResourcesEnum.user, ActionEnum.delete),
            (ResourcesEnum.sudoku, ActionEnum.read),
        ),
        RoleEnum.guest: (
            (ResourcesEnum.user, ActionEnum.read),
            (ResourcesEnum.user, ActionEnum.update),
            (ResourcesEnum.sudoku, ActionEnum.read),
        )
    }

    role_permission_id = {}
    for role_name, permission_list in role_permission.items():
        role_id = roles_db[role_name].role_id
        role_permission_id[role_name] = role_id
        for ra in permission_list:
            permission_id = permission_db[ra].permission_id
            session.add(RolePermissionModel(role_id=role_id, permission_id=permission_id))
    
    session.flush()
    return role_permission_id

def create_admin(session: Session, role_admin_id: int) -> None:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    admin = UserModel(
            role_id = role_admin_id,
            email=settings.ADMIN_EMAIL,
            password=pwd_context.hash(settings.ADMIN_PASSWORD)
            )
    session.add(admin)
    session.flush()

    result_sudoku = session.execute(select(SudokuModel.sudoku_id, SudokuModel.sudoku))
    sudoku_id, sudoku = random.choice(result_sudoku.all())

    solution_user = SudokuSolutionUserModel(
        user_id=admin.user_id,
        sudoku_id=sudoku_id,
        solution_user=sudoku,
        is_active=True
    )

    session.add(solution_user)

def seed() -> None:
    engine = create_engine(settings.DATABASE_URL_SYNC, echo=settings.DEBUG)
    session_factory = sessionmaker(engine)
    with session_factory() as session:
        if not initial_table_sudoku(session): return 

        roles = initial_role(session)
        permission = init_permision(session)
        role_permission_id = initial_role_permission(session, roles, permission)
        
        create_admin(session, role_permission_id[RoleEnum.admin])
        
        session.commit()


if __name__ == "__main__":
    seed()
