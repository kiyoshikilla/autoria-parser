from sqlalchemy import String, BigInteger
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from datetime import datetime
from typing import Optional
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass

class Car(Base):
    __tablename__ = "cars"
    
    
    id : Mapped[int] = mapped_column(primary_key=True)
    url : Mapped[str] = mapped_column(String, unique=True, nullable=False)

    ria_id : Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    title : Mapped[str] = mapped_column(String(256), nullable=False)
    price_usd : Mapped[int] = mapped_column(nullable=False)
    odometer : Mapped[int] = mapped_column(nullable=False)
    
    username : Mapped[Optional[str]] = mapped_column(String(100))
    phone_number : Mapped[Optional[str]] = mapped_column(String(20))

    image_url : Mapped[str] = mapped_column(String, nullable=False)
    car_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    car_vin: Mapped[Optional[str]] = mapped_column(String(30), unique=True, nullable=True)

    datetime_found : Mapped[datetime] =  mapped_column(
        DateTime(timezone=True),
        server_default=func.now())