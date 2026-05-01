from dataclasses import dataclass
from .enums import UuidEnum


@dataclass
class UserUuidContext:
    uuid: str
    type: UuidEnum


@dataclass
class SudokuUserContext:
    sudoku_id: int
    quality: int
    is_active: bool
    solving_time: int
    

@dataclass
class SolutionUserContext:
    sudoku: str
    solution: str
    solving_time: int