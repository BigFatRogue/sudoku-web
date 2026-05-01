from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from typing import Annotated
from fastapi import Depends

if __name__ == '__main__':
    # Для запуска через IDE
    from pathlib import Path
    import sys
    test_path = str(Path(__file__).parent.parent.parent)
    print(test_path)
    sys.path.append(test_path)

from app.core.config import settings


engine = create_async_engine(
    url=settings.DATABASE_URL_ASYNC,
    echo=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "timeout": 10,
        "command_timeout": 30,
    }
    )

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]

class Model(MappedAsDataclass, DeclarativeBase): pass

