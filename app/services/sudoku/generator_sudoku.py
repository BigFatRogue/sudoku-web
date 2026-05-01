from app.services.sudoku.pole_sudoku import PoleSudoku
from app.services.sudoku.generator_pole import GeneratorPole
from app.services.sudoku.solver_sudoku import SolverSudoku
from app.services.sudoku.tools import timer

import random
import time


class GeneratorSudoku(SolverSudoku):
    def __init__(self, pole: tuple | list | PoleSudoku, quality=21):
        super().__init__(pole)
        self.copy_poly: PoleSudoku = self.pole.copy()
        self.quality: int = quality
        self.solver_pole: list[PoleSudoku] = []
        self.buffer: list = []

    def solver_for_gen(self):
        res_1 = False

        while True:
            try:
                while not self.pole.check_solved():
                    m = self.method_1()
                    if not m:
                        self.method_2()

                if self.pole not in self.solver_pole:
                    self.solver_pole.append(self.pole)

                if len(self.solver_pole) == 1:
                    res_1 = True
                elif len(self.solver_pole) > 1:
                    res_1 = False
                    self.solver_pole = []
                    self.buffer = []
                    break

                self.pole = self.buffer.pop()

            except IndexError:
                break

        return res_1

    @timer
    def generate_sudoke(self) -> PoleSudoku:
        start = time.time()

        delay = 1
        count = 0
        while (self.pole.size**2 - self.quality) != count:
            coord = [(y, x) for y, row in enumerate(self.pole) for x, cell in enumerate(row) if cell != 0]
            while True:
                if coord:
                    y, x = random.choice(coord)
                else:
                    count = 0
                    self.pole = self.copy_poly.copy()
                    start = time.time()
                    break

                lst_copy = self.pole.copy()
                self.pole[y][x] = 0
                lst_zero = self.pole.copy()
                res1 = self.solver_for_gen()

                if res1:
                    count += 1
                    self.pole = lst_zero.copy()
                    break
                else:
                    coord.remove((y, x))
                    self.pole = lst_copy.copy()

                end = time.time()

                if end - start > delay:
                    count = 0
                    self.pole = self.copy_poly.copy()
                    start = time.time()
                    break

        return self.pole


if __name__ == '__main__':
    # Генерация поля
    pole = GeneratorPole().run()

    # Генерация головоломки
    gen = GeneratorSudoku(pole, quality=24)
    res = gen.generate_sudoke()
    # res.show()
    # SolverSudoku(res).solver().show()
    # Сохранение головоломки
    # save_sudoku(res, pole)

    # win_info.create_window('Генератор судоку', 'Готово')



