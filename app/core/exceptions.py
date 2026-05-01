class AppError(Exception):
    """Базовая ошибка приложения"""
    pass


class ValidationError(AppError):
    """Общая ошибка валидации"""
    pass