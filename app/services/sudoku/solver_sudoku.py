import random

if __name__ == '__main__':
    # Для запуска через IDE

    import sys
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent)
    print(test_path)
    sys.path.append(test_path)


from app.services.sudoku.pole_sudoku import PoleSudoku
from app.services.sudoku.tools import timer



class SolverSudoku:
    def __init__(self, pole: list | tuple | PoleSudoku):
        self.original_pole = PoleSudoku(pole) if isinstance(pole, (list, tuple, str)) else pole
        self.pole: PoleSudoku = self.original_pole.copy()

        self.buffer: list[PoleSudoku] = []
        self.solutions: list[PoleSudoku] = []
        
        self.__set_digits = {*range(1, self.pole.size + 1)}

    def get_options_cell(self, y: int, x: int) -> set[int]:
        """
        Получение списка вариантов цифр для ячейки

        Args:
            y (int): номер строки
            x (int): номер столбца

        Returns:
            set[int]: множество вариантов
        """

        return self.__set_digits \
            - set(self.pole.get_digits_row(y)) \
            - set(self.pole.get_digits_column(x)) \
            - set(self.pole.get_digits_sector_from_coords(y, x))

    def get_options_sector(self, y: int, x: int) -> tuple[list[tuple[int, int], set[int]], dict[int, int]]:
        """
        Получение списка состоящего из списка возможных цифр для ячеек сектора и координат этих ячейки

        Args:
            y (int): номер строки
            x (int): номер столбца

        Returns:
            tuple[list | dict]: _description_
        """

        lst: list[tuple[int, int], set[int]] = []
        dct = {}        
        for dy, dx in self.pole.coords_sector_from_coords_cell(y, x):
            if self.pole[dy][dx] == 0:
                options_cell = self.get_options_cell(dy, dx)
                lst.append(((dy, dx), options_cell))

                for v in options_cell:
                    if v not in dct:
                        dct[v] = 1
                    else:
                        dct[v] += 1

        return lst, dct

    def get_min_options_cell(self) -> tuple[list[set[int],], tuple[int, int]]:
        """
        Получение координат ячейки и вариантов цифр с минимальным выбором
        :return tuple({1, 2, 3...}, (y, x))
        """

        len_min_options = self.pole.size
        min_options = None

        for y, row in enumerate(self.pole):
            for x, cell in enumerate(row):
                if cell == 0:
                    var = self.get_options_cell(y, x)
                    if len(var) < len_min_options:
                        len_min_options = len(var)
                        min_options = (list(var), (y, x))

        return min_options

    def method_1(self) -> bool:
        work = 0
        paste = 1

        while paste != 0:
            paste = 0

            for y in range(0, self.pole.size, self.pole.sqrt_size):
                for x in range(0, self.pole.size, self.pole.sqrt_size):
                    lst, dct = self.get_options_sector(y, x)
                    
                    pasted = set()
                    for (dy, dx), var in lst:
                        if len(var) == 1:
                            value = var.pop()
                            # if value not in pasted:
                            self.pole[dy][dx] = value
                            paste += 1
                                # pasted.add(value)
                        else:
                            for value, count in dct.items():
                                if count == 1:
                                    if value in var:
                                        self.pole[dy][dx] = value
                                        paste += 1

            work += paste

        return work != 0

    def method_2(self) -> None:
        """
        Если method_1 и method_2 не произвели вставку, вставляется рандомно-взятое значение в ячейку с минимальным
        выбором и решение продолжается. Если выбор для ячейки ещё остался, то тогда список вносится в buffer и список
        сохраняет возможный вариант вставки и если ранее выбранная ячейка не приведёт к решению, то возьмётся
        последний добавленный список в buffer и продолжится решение.
        """

        options, (y, x) = self.pole.options if self.pole.options else self.get_min_options_cell()

        if options:
            pole_copy = self.pole.copy()
            pole_copy.options = (options, (y, x))
            self.buffer.append(pole_copy)
            self.pole[y][x] = options.pop(random.randrange(len(options)))
        else:
            pole_copy = self.buffer[-1]
            options, (y, x) = pole_copy.options

            if options:
                self.pole = pole_copy.copy()
                self.pole[y][x] = options.pop(random.randrange(len(options)))
            else:
                self.pole.options = None
                self.buffer.pop()

    def solving_sudoku(self) -> None:
        """
        Если решение не находится через m1 и m2, то тогда запускается m3 до тек пор, пока судоку не будет решено.
        :return: решённый lst
        """
        while not self.pole.check_solved():
            m = self.method_1()

            if not m:
                self.method_2()
    
    def solving_all_option_sudoku(self) -> list:
        """
        Находит все решения для судоку путём взятия разных вариантов из buffer, до тех пор
        пока он не станет равным нулю
        """

        while True:
            try:
                self.solving_sudoku()

                if self.pole not in self.solutions:
                    self.solutions.append(self.pole)
                self.pole = self.buffer.pop()

                if len(self.solutions) > 100:
                    break
            except IndexError:
                break

    @timer
    def run(self):
        self.pole.show()
        self.solving_sudoku ()
        self.pole.show()

    @timer
    def run_random(self):
        self.pole.show()
        self.solver_random()
        self.pole.show()


if __name__ == '__main__':
    # sud, sol = get_sudoku(20, 4)
    # sud = [[0, 0, 5, 0, 0, 0, 7, 0, 0],
    #        [0, 0, 0, 4, 0, 0, 0, 9, 0],
    #        [2, 0, 0, 0, 7, 0, 0, 0, 3],
    #        [0, 9, 0, 0, 0, 4, 0, 0, 0],
    #        [0, 0, 1, 0, 8, 0, 2, 0, 0],
    #        [0, 0, 0, 5, 0, 0, 0, 6, 0],
    #        [8, 0, 0, 0, 2, 0, 0, 0, 1],
    #        [0, 6, 0, 0, 0, 9, 0, 0, 0],
    #        [0, 0, 4, 0, 0, 0, 8, 0, 0]]
    sud = [[1, 2, 3, 4, 5, 6, 7, 7, 7], [4, 5, 6, 1, 2, 7, 3, 9, 8], [7, 8, 9, 8, 9, 3, 1, 2, 4], [9, 3, 5, 6, 7, 8, 4, 1, 2], [2, 6, 4, 3, 1, 9, 8, 8, 5], [8, 1, 7, 2, 4, 5, 9, 3, 6], [3, 9, 8, 7, 6, 4, 2, 5, 1], [5, 7, 2, 9, 8, 1, 6, 4, 3], [5, 7, 1, 9, 8, 2, 6, 4, 3]]
    sud = "005000700000400090200070003090004000001000200000500060800020001060009000004000800"
    solver = SolverSudoku(sud)
    # solver.run()
    # solver.run_random()
    solver.solving_all_option_sudoku()
    print(solver.pole)


