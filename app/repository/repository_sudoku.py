from random import choice
from sqlalchemy import select, and_, func, label
from sqlalchemy.orm import joinedload
from typing import Sequence

from app.schemas.scheme_sudoku import SolutionsScheme, ResponeSolutionScheme, RequestSudokuScheme
from app.db.database import SessionDep

from app.models.model_sudoku import SudokuModel, SolutionSudokuModel 
from app.models.model_users import SudokuSolutionUserModel, UserModel

from app.services.sudoku.solver_sudoku import SolverSudoku

from app.core.context import SudokuUserContext, SolutionUserContext


class SudokuRepository:
    @classmethod
    async def get_sudoku(cls, sudoku_id: int, with_solution, session: SessionDep) -> SudokuModel | None:
        if with_solution:
            result = await session.execute(select(SudokuModel).where(SudokuModel.sudoku_id == sudoku_id).options(joinedload(SudokuModel.solutions)))
            return result.unique().scalar_one_or_none()
        else:
            result = await session.execute(select(SudokuModel).where(SudokuModel.sudoku_id == sudoku_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all_sudoku(cls, with_solution: bool, session: SessionDep) -> list[SudokuModel]:
        if with_solution:
            result = await session.execute(select(SudokuModel).options(joinedload(SudokuModel.solutions)))
            return result.unique().scalars().all()
        else:
            result = await session.execute(select(SudokuModel))
            return result.scalars().all()

    @classmethod
    async def get_user_solutions(cls, user: UserModel | None, session: SessionDep) -> Sequence[SudokuUserContext]:
        """
        Полуение списка всех судоку и время затраченное на решение конкретный пользователем. 

        Если пользователь не решал судоку, то затарченное время равно 0
        """

        if user:
            result = await session.execute(
                select(
                    SudokuModel.sudoku_id, 
                    SudokuModel.quality, 
                    func.coalesce(SudokuSolutionUserModel.is_active, False).label('is_active'),
                    func.coalesce(SudokuSolutionUserModel.solving_time, 0).label('solving_time'))
                .join(
                    SudokuSolutionUserModel, 
                    and_(
                        SudokuSolutionUserModel.sudoku_id == SudokuModel.sudoku_id,
                        SudokuSolutionUserModel.user_id == user.user_id
                        ),
                        isouter=True
                    )
                )
        else:            
            result = await session.execute(
                select(
                    SudokuModel.sudoku_id,
                    SudokuModel.quality,
                    False,
                    0
                )
            )

        return [SudokuUserContext(*result) for result in result.all()]

    @classmethod
    async def set_active_sudoku_user(cls, user: UserModel, sudoku_id: int, session: SessionDep) -> SolutionUserContext:
        """
        Переключение активного пользовательское решение на другое пользовательское решение
        """
        result_active_solution = await session.execute(
            select(SudokuSolutionUserModel)
            .where(SudokuSolutionUserModel.user_id == user.user_id, SudokuSolutionUserModel.is_active == True))
        
        solution_user = result_active_solution.scalars().first()
        if solution_user:
            solution_user.is_active = False
            session.add(solution_user)

        # Если есть пользовательское решение, то получить судоку + решение
        result_user_solution = await session.execute(
            select(SudokuModel.sudoku, SudokuSolutionUserModel.solution_user, SudokuSolutionUserModel.solving_time)
            .join(SudokuModel, SudokuModel.sudoku_id == SudokuSolutionUserModel.sudoku_id)
            .where(SudokuSolutionUserModel.user_id == user.user_id, SudokuModel.sudoku_id == sudoku_id)
        )

        sudoku_solution = result_user_solution.one_or_none()
        if sudoku_solution:
            await cls.set_active_sudoku(user=user, sudoku_id=sudoku_id, is_active=True, session=session)
            return SolutionUserContext(*sudoku_solution)
        else:
            sudoku = await cls.add_sudoku_for_user(user=user, sudoku_id=sudoku_id, session=session)
            return SolutionUserContext(sudoku=sudoku, solution=sudoku, solving_time=0)
    
    @classmethod
    async def set_active_sudoku(cls, user: UserModel, sudoku_id: int, session: SessionDep, is_active: bool = True) -> None:
        """
        Присваивания активности для пользовательского решения 
        """
        solution_user = await session.execute(
        select(SudokuSolutionUserModel)
        .where(SudokuSolutionUserModel.user_id == user.user_id, SudokuSolutionUserModel.sudoku_id == sudoku_id)
        )

        solution = solution_user.scalars().first()
            
        solution.is_active = is_active
        session.add(solution)
        await session.commit()

    @classmethod
    async def add_sudoku_for_user(cls, user: UserModel, sudoku_id: int, session: SessionDep) -> str:
        """
        Добавление пользователю новое судоку
        """
        result_sudoku = await session.execute(select(SudokuModel.sudoku).where(SudokuModel.sudoku_id == sudoku_id))
        sudoku = result_sudoku.scalar_one()
        solution_user = SudokuSolutionUserModel(
            user_id=user.user_id,
            sudoku_id=sudoku_id,
            solution_user=sudoku,
            is_active=True
        )
        session.add(solution_user)
        await session.commit()

        return sudoku

    @classmethod
    async def update_solution_user(
        cls,
        user: UserModel,  
        solution_data: ResponeSolutionScheme, 
        session: SessionDep) -> None:
        """
        Обновление судоку пользователя
        """
        query = select(SudokuSolutionUserModel).where(
            SudokuSolutionUserModel.user_id == user.user_id, 
            SudokuSolutionUserModel.sudoku_id == solution_data.sudoku_id)

        result = await session.execute(query)
        solution = result.scalar_one_or_none()

        if solution:
            solution.solution_user=solution_data.solution
            solution.solving_time=solution_data.solving_time
            solution.is_solved=solution_data.is_solved
            solution.is_active=solution_data.is_active
        else:
            solution = SudokuSolutionUserModel(
                user_id=user.user_id,
                sudoku_id=solution_data.sudoku_id,
                solution_user=solution_data.solution,
                solving_time=solution_data.solving_time,
                is_solved=solution_data.is_solved,
                is_active=solution_data.is_active
            )
        
        session.add(solution)
        await session.commit()

    @classmethod
    async def get_solution(cls, sudoku_id: int | None, sudoku: str, session: SessionDep) -> list[str]:
        """
        Получить решение судоку из БД или решение судоку
        
        """
        if sudoku_id is not None:
            result = await session.execute(select(SolutionSudokuModel.solution).filter_by(sudoku_id=sudoku_id))
            solution = result.scalars().all()
            return solution
        else:
            solver = SolverSudoku(sudoku)
            solver.solving_all_option_sudoku()
            solution = [i.to_string_line() for i in solver.solutions]
        
        return solution