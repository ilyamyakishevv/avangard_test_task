from typing import Optional

from pydantic import BaseModel


class CurrenciesPairs(BaseModel):
    user_currency: str
    max_treshold: float
    min_treshold: float


class CurrenciesPairsCreateDB(CurrenciesPairs):
    user_tg_id: int


class CurrenciesPairsResponse(CurrenciesPairs):
    id: int
    user_tg_id: int

    class Config:
        from_attributes = True


class CurreciesPairsUpdate(BaseModel):
    max_treshold: Optional[float] = None
    min_treshold: Optional[float] = None
