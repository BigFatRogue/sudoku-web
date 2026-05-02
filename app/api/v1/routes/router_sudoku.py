from fastapi import APIRouter, status, HTTPException

from app.db.database import SessionDep

from app.schemas.scheme_sudoku import SudokuScheme, ResponeSolutionScheme, SolutionsScheme, RequestSudokuScheme

from app.repository.repository_sudoku import SudokuRepository
from app.repository.repository_auth import AuthRepository

from app.core.enums import TagsEnum
from app.core.context import SolutionUserContext

from ..deps import UserUuidDep 


sudoku_router = APIRouter(prefix='/sudoku', tags=[TagsEnum.sudoku])


@sudoku_router.get(
        path='/sudoku',
        summary='Получить судоку по id'
        )
async def get_sudoku(session: SessionDep, sudoku_id: int, with_solution: bool=False) -> SudokuScheme:
    sudoku = await SudokuRepository.get_sudoku(session=session, sudoku_id=sudoku_id, with_solution=with_solution)
    if sudoku:
        if with_solution:
            return SudokuScheme(
                sudoku_id=sudoku.sudoku_id, 
                sudoku=sudoku.sudoku, 
                quality=sudoku.quality, 
                solution=[sol.solution for sol in sudoku.solutions]
                )
        else:
            return SudokuScheme(sudoku_id=sudoku.sudoku_id, sudoku=sudoku.sudoku, quality=sudoku.quality)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Судоку с такми id не существует')


@sudoku_router.get(
        path='/all',
        summary='Список всех судоку в БД'
        )
async def get_all_sudoku(session: SessionDep, with_solution: bool=False) -> list[SudokuScheme]:
    all_sudoku = await SudokuRepository.get_all_sudoku(with_solution=with_solution, session=session)
    if with_solution:
        return [SudokuScheme(
            sudoku_id=sudoku.sudoku_id, 
            sudoku=sudoku.sudoku, 
            quality=sudoku.quality, 
            solution=[sol.solution for sol in sudoku.solutions]) 
            for sudoku in all_sudoku]
    else:
        return [SudokuScheme(sudoku_id=sudoku.sudoku_id, sudoku=sudoku.sudoku, quality=sudoku.quality) for sudoku in all_sudoku]


@sudoku_router.get(
        path='/solution', 
        summary='Получение решения судоку из БД или введённое пользователем')
async def get_solution(sudoku: str, session: SessionDep, sudoku_id: int | None = None) -> SolutionsScheme:
    solution = await SudokuRepository.get_solution(sudoku_id=sudoku_id, sudoku=sudoku, session=session)
    return SolutionsScheme(solutions=solution)


@sudoku_router.get(
        path='/list_user', 
        summary='Получения списка судоку текущем пользователем',
        description='Получения списка всех судоку с учётом затраченного времени пользователем на их решения')
async def get_sudoku_me(user_uuid: UserUuidDep, session: SessionDep) -> list[ResponeSolutionScheme]:
    if not user_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = await AuthRepository.get_user(uuid=user_uuid.uuid, type_uuid=user_uuid.type, session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    list_sudoku = await SudokuRepository.get_user_solutions(user=user, session=session)

    response: list[ResponeSolutionScheme] = []
    for sudoku_context in list_sudoku:
        response.append(
            ResponeSolutionScheme(
                sudoku_id=sudoku_context.sudoku_id,
                quality=sudoku_context.quality,
                solving_time=sudoku_context.solving_time,
                is_active=sudoku_context.is_active
            )
        )
        
    return response
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@sudoku_router.get(
        path='/active_sudoku_user/{sudoku_id}', 
        summary='Получения решения пользователя'
        )
async def get_active_sudoku_user(sudoku_id: int, user_uuid: UserUuidDep, session: SessionDep) -> ResponeSolutionScheme:
    if not user_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = await AuthRepository.get_user(uuid=user_uuid.uuid, type_uuid=user_uuid.type, session=session)
    if not user:   
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)         
    solution_user: SolutionUserContext = await SudokuRepository.set_active_sudoku_user(user=user, sudoku_id=sudoku_id, session=session)

    return ResponeSolutionScheme(
        sudoku_id=sudoku_id, 
        sudoku=solution_user.sudoku, 
        solution=solution_user.solution,
        solving_time=solution_user.solving_time,
        is_active=True)
    

@sudoku_router.post(
        path='/update_solution',
        summary='Обновление решений пользователя')
async def update_solution(
    user_uuid: UserUuidDep, 
    solution_data: ResponeSolutionScheme, 
    session: SessionDep) -> dict[str, int]:
    
    if not user_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user = await AuthRepository.get_user(uuid=user_uuid.uuid, type_uuid=user_uuid.type, session=session)
    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    await SudokuRepository.update_solution_user(user=user, solution_data=solution_data,session=session)
    return {'succses': True}
    
    

