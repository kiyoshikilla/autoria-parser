from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base, Car
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
import os

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def upsert_car(car_data:dict, session:AsyncSession):
    
    from sqlalchemy.exc import IntegrityError
    car_query = insert(Car).values(car_data)
    car_query = car_query.on_conflict_do_update(
        index_elements=["ria_id"],
        set_=dict(
            price_usd=car_query.excluded.price_usd,
            odometer=car_query.excluded.odometer,
            username=car_query.excluded.username,
            phone_number=car_query.excluded.phone_number,
            title=car_query.excluded.title,
            image_url=car_query.excluded.image_url,
            car_number=car_query.excluded.car_number,
            car_vin=car_query.excluded.car_vin
        )
    )
    try:
        await session.execute(car_query)
        await session.commit()
    except IntegrityError as e:
        print(f"[DB ERROR] Не вдалося вставити/оновити авто: {car_data.get('url')} — {e}")
        await session.rollback()
    