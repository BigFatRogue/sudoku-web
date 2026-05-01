from typing import Self

if __name__ == '__main__':
    # Для запуска через IDE
    from pathlib import Path
    import sys
    test_path = str(Path(__file__).parent.parent.parent)
    print(test_path)
    sys.path.append(test_path)

from app.services.sudoku.exceptions import TypeDataSudokuError, SizeCountSudokuError, SizeSqrtSudokuError, SizeLimitSudokuError, DublicateError, DigitError, EmptySudokuError


class PoleSudoku:
    """
    Обёртка для матрица N² x N² для валидации и доступа к данным
    """
    def __init__(self, pole: list[list[int]] | tuple[tuple[int]] | str, coords_sectors: dict[int, tuple[tuple[int, int]]] | None=None, need_validate: bool = True):
        self.pole = self.__validate_init_pole(pole)
        
        self.size: int = len(self.pole)
        self.sqrt_size: int = int(self.size ** 0.5)
        self.coords_sectors: dict[int, tuple[tuple[int, int]]] = self.__calc_coords_sectors() if coords_sectors is None else coords_sectors

        if need_validate:
            self.__validate_dublicate_pole()

        self.options: tuple[list[set[int],], tuple[int, int]] | None = None

    def __validate_init_pole(self, pole: list[list[int]] | tuple[tuple[int]] | str) -> list[list[int]] | tuple[tuple[int]]  | None:
        """
        Проверка корректности данных при инициализации
        """

        if isinstance(pole, str):
            pole = self.__str_to_list(pole)

        sqrt_size_row = len(pole)**0.5

        if not isinstance(pole, (list, tuple)) and not isinstance(pole[0], (list, tuple)):
            raise TypeDataSudokuError()
        
        elif len(pole) != len(pole[0]):
            raise SizeCountSudokuError()
        
        elif int(sqrt_size_row) - sqrt_size_row != 0:
            raise SizeSqrtSudokuError()
        
        elif int(sqrt_size_row) not in (2, 3, 4, 5):
            raise SizeLimitSudokuError()

        self.__correct_str_to_int(pole)

        if not any([value != 0 for row in pole for value in row]):
            raise EmptySudokuError()

        return pole

    def __correct_str_to_int(self, pole: list[list[int]] | tuple[tuple[int]]) -> None:
        sqrt_size_row = len(pole)**0.5

        for y, row in enumerate(pole):
            for x, value in enumerate(row):
                if isinstance(value, str):
                    if value.isdigit():
                        value = int(value)
                        if not 0 <= value <= sqrt_size_row:
                            raise TypeError(f'Значение в {x=}, {y=}, {value=} не должно быть не более {len(pole)}')
                        pole[y][x] = value
                    else:
                        raise TypeError(f'Значение в {x=}, {y=}, {value} должно быть числовым значенем ') 

    def __str_to_list(self, sudoku: str) -> list[list[int]] | None:
        size = len(sudoku) 
        
        if size not in (16, 81, 256, 625):
            raise SizeSqrtSudokuError('Поле должно иметь размерность равную квадрату целого числа')

        sqrt_size = int(size**0.5)

        pole = []
        row = []
        for value in sudoku:
            if len(row) == sqrt_size:
                pole.append(row)
                row = []
            if not value.isdigit():
                raise DigitError()
            row.append(int(value))
        pole.append(row)
        
        return pole

    def __calc_coords_sectors(self) -> dict[int, tuple[tuple[int, int]]]:
        """
        Получение координат всех секторов.
        :return: {1: ((y, x),..) ... self.size: ((y, x),..)}
        """

        s = 0
        dct = {}
        for y in range(0, self.size, self.sqrt_size):
            for x in range(0, self.size, self.sqrt_size):
                dct[s] = tuple((dy, dx) for dy in range(y, y + self.sqrt_size) for dx in range(x, x + self.sqrt_size))
                s += 1
        return dct

    def __validate_dublicate_pole(self) -> bool:
        """
        Проверка на наличие дубликатов в строках и секторах
        """

        for size in range(self.size):
            row = self.get_digits_row(size)
            if len(row) != len(set(row)):
                raise DublicateError(f'Имеются дубликаты в строке {size}')
            
            col = self.get_digits_column(size)
            if len(col) != len(set(col)):
                raise DublicateError(f'Имеются дубликаты в столбце {size}')
            
            sector = self.get_digits_sector_from_sector(size)
            if len(sector) != len(set(sector)):
                raise DublicateError(f'Имеются дубликаты в секторе {size}')
            
    def get_digits_row(self, row: int) -> tuple[int]:
        """
        Получение списка состоящего из чисел в заданной строке списка

        Args:
            row (int): номер строки

        Returns:
            tuple[int]: список заполненых чисел в данной строке
        """

        return tuple(i for i in self.pole[row] if i != 0)
    
    def get_digits_column(self, col: int) -> tuple[int]:
        """
        Получение множества состоящего из чисел в заданной колонке списка
        
        :return: set[int]
        """

        return tuple(self.pole[y][col] for y in range(self.size) if self.pole[y][col] != 0)

    def get_digits_sector_from_sector(self, sector: int) -> tuple[int]:
        """
        Получение множества состоящие из цифр для заданного сектора
        """
        return tuple(self.pole[y][x] for y, x in self.coords_sectors[sector] if self.pole[y][x] != 0)

    def get_digits_sector_from_coords(self, y: int, x: int) -> tuple[int]:
        """
        Получение множества состоящего из цифр заданного сектора БЕЗ нулей

        Args:
            y (int): номер строки
            x (int): номер столбца

        Returns:
            tuple[int]: массив цифр для сектора БЕЗ нулей
        """

        sector = y // self.sqrt_size * self.sqrt_size + x // self.sqrt_size
        return tuple(self.pole[y][x] for y, x in self.coords_sectors[sector] if self.pole[y][x] != 0)

    def coords_sector_from_coords_cell(self, y: int, x: int) -> tuple[tuple[int, int]]:
        """
        Получение кординат ячеек сектора по координате одной ячейки

        Args:
            y (int): номер строки
            x (int): номер столбца

        Returns:
            tuple[tuple[int, int]]: массив координат
        """
        sector = y // self.sqrt_size * self.sqrt_size + x // self.sqrt_size
        return tuple((y, x) for y, x in self.coords_sectors[sector])

    def check_solved(self) -> bool:
        'Проверяет есть ли нули в строчках. Если есть, значит судоку ещё не решено'
        for row in self.pole:
            if 0 in row:
                return False
        return True

    def show(self) -> None:
        """
        Вывод поля в консоль
        """
        for row in self.pole:
            for cell in row:
                print(cell, end='  ')
            print()
        print()

    def copy(self) -> Self:
        """
        Копирования и возврат Self

        :return: _type_: Self
        """
        copy_pole = [[value for value in row] for row in self.pole]
        return self.__class__(copy_pole, coords_sectors=self.coords_sectors, need_validate=False)

    def to_string_line(self) -> str:
        return ''.join([str(value) for row in self.pole for value in row])

    def __getitem__(self, item: int):
        return self.pole[item]

    def __setitem__(self, key: int, value: int):
        self.pole[key] = value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.pole == other.pole
        raise TypeError('Для сравнения можно передать только объект Sudoku')

    def __str__(self):
        return '\n'.join(['  '.join(map(str, row)) for row in self.pole]) + '\n'

    def __repr__(self):
        return str(self.pole)


if __name__ == '__main__':
    # pole = [[0, 0, 0, 1, 6, 0, 3, 2, 0], [0, 0, 0, 0, 0, 3, 0, 0, 0], [0, 0, 6, 0, 0, 0, 0, 5, 0], [0, 0, 5, 2, 0, 0, 0, 0, 8], [0, 4, 0, 0, 0, 0, 0, 1, 0], [3, 0, 0, 0, 0, 5, 0, 0, 4], [0, 0, 0, 0, 0, 0, 0, 6, 7], [9, 0, 0, 4, 0, 8, 0, 0, 0], [0, 0, 0, 5, 0, 0, 0, 0, 0]]
    # pole = [[0, 0, 5, 0, 0, 0, 7, 0, 0],
    #        [0, 0, 0, 4, 0, 0, 0, 9, 0],
    #        [2, 0, 0, 0, 7, 0, 0, 0, 3],
    #        [0, 9, 0, 0, 0, 4, 0, 0, 0],
    #        [0, 0, 1, 0, 8, 0, 2, 0, 0],
    #        [0, 0, 0, 5, 0, 0, 0, 6, 0],
    #        [8, 0, 0, 0, 2, 0, 0, 0, 1],
    #        [0, 6, 0, 0, 0, 9, 0, 0, 0],
    #        [0, 0, 4, 0, 0, 0, 8, 0, 0]]
    pole = "029080300700000104000000080100300000000098701000002500200070800900000050080105230"

    sud = PoleSudoku(pole)
    sud.show()
