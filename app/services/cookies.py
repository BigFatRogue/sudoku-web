from fastapi import Response, Request, HTTPException, status
import uuid

from app.core.enums import UuidEnum


def create_uuid_cookie(key: UuidEnum, response: Response, max_age: int=60*60*24*30) -> str:
    """
    Создание в cookie guest_uuid или session_uuid
    """
    response.delete_cookie(key)
    key_uuid = str(uuid.uuid4())
    response.set_cookie(
        key=key,
        value=key_uuid,
        max_age=max_age
        )
    return key_uuid

def delete_cookie(key: UuidEnum, response: Response) -> None:
    response.delete_cookie(key)
