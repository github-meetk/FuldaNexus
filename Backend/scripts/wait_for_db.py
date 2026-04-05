import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

MAX_ATTEMPTS = 30
SLEEP_SECONDS = 2


async def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite+") else {}

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            engine = create_async_engine(
                database_url,
                connect_args=connect_args,
                pool_pre_ping=True,
            )
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            print(f"Database connection established on attempt {attempt}.")
            return
        except Exception as exc:
            print(f"Database not ready (attempt {attempt}/{MAX_ATTEMPTS}): {exc}")
            await asyncio.sleep(SLEEP_SECONDS)
    raise RuntimeError("Database never became available")


if __name__ == "__main__":
    asyncio.run(main())
