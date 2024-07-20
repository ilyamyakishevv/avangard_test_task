from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import currrencies_crud
from database import get_async_session
from schemas import (
    CurrenciesPairsResponse,
    CurrenciesPairsCreateDB,
    CurreciesPairsUpdate,
)

router = APIRouter(
    prefix="/currencies_pairs",
    tags=["Currencies Pairs"],
)


@router.get("/all/", response_model=List[CurrenciesPairsResponse])
async def get_currencies_pairs(db: AsyncSession = Depends(get_async_session)):
    return await currrencies_crud.read_all(db=db)


@router.get("/{tg_id}/", response_model=List[CurrenciesPairsResponse])
async def get_user_currencies_pairs(tg_id: int, db: AsyncSession = Depends(get_async_session)):
    return await currrencies_crud.read_user_pairs(db=db, tg_id=tg_id)


@router.post("/create_pair/", response_model=CurrenciesPairsResponse)
async def post_currencies_pairs(
    create_data: CurrenciesPairsCreateDB,
    db: AsyncSession = Depends(get_async_session),
):
    return await currrencies_crud.create(db=db, create_schema=create_data)


@router.patch("/{obj_id}/", response_model=CurrenciesPairsResponse)
async def update_currencies_pair(
    obj_id: int,
    update_data: CurreciesPairsUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    return await currrencies_crud.update(db=db, obj_id=obj_id, update_schema=update_data)


@router.delete("/{obj_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_currencies_pair(
    obj_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    return await currrencies_crud.delete(db=db, obj_id=obj_id)
