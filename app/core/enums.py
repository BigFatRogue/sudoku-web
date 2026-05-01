from enum import Enum, StrEnum


class UuidEnum(StrEnum):
    guest_uuid: str = 'guest_uuid'
    session_uuid: str = 'session_uuid'


class TagsEnum(StrEnum):
    sudoku: str = 'Sudoku'
    users: str = 'Users'
    auth: str = 'Auth'