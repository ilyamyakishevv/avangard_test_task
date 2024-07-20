from datetime import datetime

from sqlalchemy import Float, func, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CurrenciesPairs(Base):
    __tablename__ = "currencies_pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_currency: Mapped[str] = mapped_column(String)
    user_tg_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    max_treshold: Mapped[float] = mapped_column(Float)
    min_treshold: Mapped[float] = mapped_column(Float)
