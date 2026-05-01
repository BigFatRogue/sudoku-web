from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.database import Model



class SudokuModel(Model):
    __tablename__ = 'sudoku'

    sudoku_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    sudoku: Mapped[str]
    quality: Mapped[int]
    
    solutions: Mapped[list['SolutionSudokuModel']] = relationship(back_populates='sudoku', cascade="all", init=False)
    

class SolutionSudokuModel(Model):
    __tablename__ = 'solution'

    solution_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    solution: Mapped[str]
    sudoku_id: Mapped[int] = mapped_column(ForeignKey('sudoku.sudoku_id'), init=False)

    sudoku: Mapped['SudokuModel'] = relationship(back_populates="solutions", init=False)




