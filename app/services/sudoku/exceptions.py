from app.core.exceptions import ValidationError


class EmptySudokuError(ValidationError):
    def __init__(self, message='Поле не должно быть пустым'):
        super().__init__(message)


class TypeDataSudokuError(ValidationError):
    def __init__(self, message='Поле должно иметь тип list | tuple | str'):
        super().__init__(message)


class SizeCountSudokuError(ValidationError):
    def __init__(self, message='Количество строк должно совпадать с количество столбцов'):
        super().__init__(message)


class SizeSqrtSudokuError(ValidationError):
    def __init__(self, message='Поле должно иметь размерность равную квадрату целого числа'):
        super().__init__(message)


class SizeLimitSudokuError(ValidationError):
    def __init__(self, message='Поле должноть размерностью не более 4х4...25х25'):
        super().__init__(message)


class DublicateError(ValidationError): ...


class DigitError(ValidationError):
    def __init__(self, message='Значения поля должны быть целые числа'):
        super().__init__(message)