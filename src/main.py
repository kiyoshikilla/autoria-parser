from .database import create_db
import asyncio

async def main():
    await create_db()


if __name__ == "__main__":
    asyncio.run(main())

