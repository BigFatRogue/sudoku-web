#  Генерация заполненного поля N² x N²

import random
from app.services.sudoku.pole_sudoku import PoleSudoku
from app.services.sudoku.solver_sudoku import SolverSudoku


class GeneratorPole:
    def __init__(self, size: int = 9):
        self.pole = [[0] * size for y in range(size)]
        self.size = size
        self.sqrt_size = int(size**0.5)

    def get_random_sector(self):
        digit = list(range(1, self.size + 1))
        random.shuffle(digit)

        for y in range(self.sqrt_size):
            for x in range(self.sqrt_size):
                self.pole[y][x] = digit[y*self.sqrt_size + x]

    # @timer
    def run(self) -> PoleSudoku:
        self.get_random_sector()

        if self.size < 10:
            return SolverSudoku(self.pole).solver_random()
        return SolverSudoku(self.pole).solving_sudoku ()


if __name__ == '__main__':
    gen = GeneratorPole()
    pole = gen.run()
    pole.show()

    