import asyncio
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


if __name__ == '__main__':
    # Для запуска через IDE

    import sys
    test_path = str(Path(__file__).parent.parent.parent)
    sys.path.append(test_path)


from app.core.config import settings


PATH_DATASETD = str(Path(__file__).parent.parent / 'services' / 'dataset.json')


async def create_database_exists(name_db: str):
    engine = create_async_engine(settings.DATABASE_BASE_URL_ASYNC, echo=settings.DEBUG)
    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{name_db}'")
        )
        if not result.fetchone():
            await conn.execute(text(f"CREATE DATABASE {name_db}"))
            print(f"База данных {name_db} создана")
        else:
            print(f"База данных {name_db} уже существует")
    await engine.dispose()



if __name__ == "__main__":
    asyncio.run(create_database_exists(settings.POSTGRES_DB))
