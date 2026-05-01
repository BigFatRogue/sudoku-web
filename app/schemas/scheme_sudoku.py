from pydantic import BaseModel

   
class SolutionsScheme(BaseModel):
    solutions: list[str]


class SudokuScheme(BaseModel):
    sudoku_id: int
    sudoku: str
    quality: int
    solution: list[str] | None = None


class RequestSudokuScheme(BaseModel):
    sudoku_id: int | None = None
    sudoku: str | None = None
    

class ResponeSolutionScheme(RequestSudokuScheme):
    quality: int | None = None
    solving_time: int | None = None
    solution: str | None = None
    is_active: bool = False
    is_solved: bool = False
